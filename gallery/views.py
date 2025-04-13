from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Event, Photo
from .forms import EventForm, PhotoForm, PhotoUploadForm
from users.decorators import admin_required
import logging # Import the logging library

# Get a logger instance for this module
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
    event = get_object_or_404(Event, pk=event_pk)
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES, event_instance=event)
        if form.is_valid():
            images = request.FILES.getlist('images')
            captions_text = form.cleaned_data.get('captions', '')
            captions = captions_text.splitlines()
            
            successful_uploads = 0
            errors_occurred = False # Flag to track if any error happened

            for i, image in enumerate(images):
                caption = captions[i].strip() if i < len(captions) else ''
                logger.info(f"Attempting to upload photo: {image.name} for event {event_pk}") # Log start
                try:
                    Photo.objects.create(
                        event=event,
                        image=image, # This triggers the Azure upload via storage backend
                        caption=caption,
                        uploaded_by=request.user
                    )
                    logger.info(f"Successfully created Photo object for: {image.name}") # Log success
                    successful_uploads += 1
                except Exception as e:
                    errors_occurred = True # Set the flag
                    # --- LOG THE FULL EXCEPTION ---
                    logger.error(
                        f"!!! FAILED to create Photo object/upload '{image.name}' to Azure for event {event_pk} !!!",
                        exc_info=True # This includes the full traceback in the log
                    )
                    # Keep the user message, but the log is more important for debugging
                    messages.error(request, f"Error saving photo '{image.name}'. Please check logs.")

            # Provide summary feedback based on errors
            if errors_occurred:
                 messages.warning(request, f"Completed upload process with errors. {successful_uploads} out of {len(images)} photos might have been saved.")
            elif successful_uploads > 0:
                 messages.success(request, f'{successful_uploads} photo(s) uploaded successfully!')
            else:
                 # Should not happen if form is valid and images list is not empty, but good failsafe
                 messages.error(request, "No photos were processed.")

            # Always redirect back to the detail page after processing
            return redirect('gallery:event_detail', pk=event.pk)
        else:
            # --- LOG FORM ERRORS ---
            logger.warning(f"Photo upload form invalid for event {event_pk}: {form.errors.as_json()}")
            messages.error(request, f"Please correct the errors below: {form.errors}")
    else:
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
