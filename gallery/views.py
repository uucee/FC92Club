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

# gallery/views.py
# ... imports and logger setup ...

""" @admin_required
def photo_upload(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    form = None # Initialize form variable

    if request.method == 'POST':
        # --- START NEW LOGGING ---
        logger.info(f"--- Handling POST for event {event_pk} ---")
        logger.info(f"request.POST contents: {request.POST}")
        logger.info(f"request.FILES contents: {request.FILES}")
        # --- END NEW LOGGING ---

        form = PhotoUploadForm(request.POST, request.FILES, event_instance=event)

        # --- Log form validity AND file list immediately after check ---
        form_is_valid = form.is_valid()
        logger.info(f"Result of form.is_valid(): {form_is_valid}")
        if form_is_valid:
            images = request.FILES.getlist('images') # Get the list *after* validation
            logger.info(f"Contents of images list (from getlist): {images}") # Log the list itself
            # --- REST OF YOUR if form_is_valid BLOCK ---
            captions_text = form.cleaned_data.get('captions', '')
            captions = captions_text.splitlines()

            successful_uploads = 0
            errors_occurred = False

            for i, image in enumerate(images):
                caption = captions[i].strip() if i < len(captions) else ''
                logger.info(f"Attempting to upload photo: {image.name} for event {event_pk}")
                try:
                    Photo.objects.create(
                        event=event,
                        image=image,
                        caption=caption,
                        uploaded_by=request.user
                    )
                    logger.info(f"Successfully created Photo object for: {image.name}")
                    successful_uploads += 1
                except Exception as e:
                    errors_occurred = True
                    logger.error(
                        f"!!! FAILED to create Photo object/upload '{image.name}' to Azure for event {event_pk} !!!",
                        exc_info=True
                    )
                    messages.error(request, f"Error saving photo '{image.name}'. Please check logs.")

            if errors_occurred:
                 messages.warning(request, f"Completed upload process with errors. {successful_uploads} out of {len(images)} photos might have been saved.")
            elif successful_uploads > 0:
                 messages.success(request, f'{successful_uploads} photo(s) uploaded successfully!')
            else:
                 # This message will now appear if images list was empty
                 messages.info(request, "Upload processed, but no new photos were saved (was the file list empty?).")

            return redirect('gallery:event_detail', pk=event.pk)
            # --- END OF if form_is_valid BLOCK ---
        else:
            # --- Log form errors if invalid ---
            logger.warning(f"Photo upload form invalid for event {event_pk}: {form.errors.as_json()}")
            messages.error(request, f"Please correct the errors below: {form.errors}")
    else: # if request.method != 'POST':
        form = PhotoUploadForm(event_instance=event)

    # Ensure form is passed to context even if POST fails validation
    return render(request, 'gallery/photo_upload.html', {'form': form, 'event': event})
 """
 
# ===== TEMPORARY SIMPLIFIED DEBUGGING VIEW =====
@admin_required
def photo_upload(request, event_pk):
    # Try getting event just to ensure basic DB access works if needed later
    try:
         event = get_object_or_404(Event, pk=event_pk)
         event_title = event.title
    except Exception as e:
         logger.error(f"Simplified view: Failed to get event {event_pk}", exc_info=True)
         event_title = f"Event PK {event_pk} (Error finding)"

    logger.info(f"--- >>> ENTERING SIMPLIFIED photo_upload view for event {event_pk} ({event_title}) ---")
    logger.info(f"Request method: {request.method}")

    if request.method == 'POST':
        logger.info("--- >>> HANDLING POST request (SIMPLIFIED View) ---")
        post_data_summary = str(request.POST)[:200] # Log only first 200 chars
        files_data_summary = str(request.FILES)[:200] # Log only first 200 chars
        logger.info(f"Simplified request.POST (summary): {post_data_summary}")
        logger.info(f"Simplified request.FILES (summary): {files_data_summary}")
        # Return a simple success message immediately, bypassing forms etc.
        return HttpResponse(f"SIMPLIFIED VIEW: Received POST for event {event_pk}. Check logs.", status=200)
    else: # GET request
         logger.info("--- >>> HANDLING GET request (SIMPLIFIED View) ---")
         # Return a simple message, don't bother rendering the actual form
         return HttpResponse(f"SIMPLIFIED VIEW: Displaying upload form page for event {event_pk}. Submit the form to test POST logging.", status=200)
# ===== END OF TEMPORARY SIMPLIFIED DEBUGGING VIEW =====
 
 
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
