from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from .models import Event, Photo
from .forms import EventForm, PhotoForm, PhotoUploadForm
from users.decorators import admin_required
import logging
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def event_list(request):
    events = Event.objects.all().order_by('-date')
    paginator = Paginator(events, 9)  # Show 9 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'gallery/event_list.html', {'page_obj': page_obj})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    photos = event.photos.all().order_by('-uploaded_at')
    return render(request, 'gallery/event_detail.html', {
        'event': event,
        'photos': photos
    })

@admin_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('gallery:event_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'gallery/event_form.html', {'form': form})

@admin_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('gallery:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'gallery/event_form.html', {'form': form, 'event': event})

@admin_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('gallery:event_list')
    return render(request, 'gallery/event_confirm_delete.html', {'event': event})

@admin_required
def photo_upload(request, event_pk):
    logger.info(f"--- >>> Entered photo_upload view for event {event_pk}. Method: {request.method} <<< ---")
    event = get_object_or_404(Event, pk=event_pk)
    form = None

    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES, event_instance=event)
        logger.info(f"--- Handling POST for event {event_pk} ---")
        logger.info(f"request.POST contents: {request.POST}")
        logger.info(f"request.FILES contents: {request.FILES}")

        if form.is_valid():
            logger.info(f"Result of form.is_valid(): True")
            images = request.FILES.getlist('images')
            logger.info(f"Contents of images list (from getlist): {images}")
            captions_text = form.cleaned_data.get('captions', '')
            captions = captions_text.splitlines()

            for i, image_file in enumerate(images):
                caption = captions[i].strip() if i < len(captions) else ''
                logger.info(f"Attempting to process photo: {image_file.name} for event {event.pk}")

                try:
                    photo_instance = Photo(
                        event=event,
                        image=image_file,
                        caption=caption,
                        uploaded_by=request.user
                    )
                    photo_instance.save()
                    logger.info(f"Successfully SAVED Photo object for: {image_file.name} (PK: {photo_instance.pk})")

                except Exception as e:
                    logger.error(f"!!! FAILED to save/upload photo '{image_file.name}' for event {event.pk} !!!", exc_info=True)
                    messages.error(request, f"Error saving photo '{image_file.name}'. Please check logs.")
                    continue

            messages.success(request, f'{len(images)} photo(s) processed successfully!')
            return redirect('gallery:event_detail', pk=event.pk)
        else:
            logger.warning(f"Form validation failed: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        logger.info(f"--- >>> Entered photo_upload view for event {event_pk}. Method: GET <<< ---")
        form = PhotoUploadForm(event_instance=event)

    return render(request, 'gallery/photo_upload.html', {'form': form, 'event': event})

@admin_required
def photo_edit(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if request.method == 'POST':
        form = PhotoForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Photo updated successfully!')
            return redirect('gallery:event_detail', pk=photo.event.pk)
    else:
        form = PhotoForm(instance=photo)
    return render(request, 'gallery/photo_edit.html', {'form': form, 'photo': photo})

@admin_required
def photo_delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    event_pk = photo.event.pk
    if request.method == 'POST':
        photo.delete()
        messages.success(request, 'Photo deleted successfully!')
        return redirect('gallery:event_detail', pk=event_pk)
    return render(request, 'gallery/photo_confirm_delete.html', {'photo': photo})
