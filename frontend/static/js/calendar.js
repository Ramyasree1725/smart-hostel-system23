(function () {
  'use strict';

  const csrfToken = getCookie('csrftoken');
  let calendar;
  let resources = [];

  function getCookie(name) {
    let v = null;
    if (document.cookie) {
      document.cookie.split(';').forEach(c => {
        c = c.trim();
        if (c.startsWith(name + '=')) v = decodeURIComponent(c.substring(name.length + 1));
      });
    }
    return v;
  }

  async function api(url, options = {}) {
    const opts = {
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        ...(options.headers || {}),
      },
      ...options,
    };
    const res = await fetch(url, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg = data.detail || data.non_field_errors?.[0] || JSON.stringify(data) || res.statusText;
      throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
    return data;
  }

  async function loadResources() {
    try {
      const data = await api('/api/resources/resources/');
      resources = data.results || data;
      renderResourceCards(resources);
      populateSelectOptions(resources);
    } catch (e) {
      console.warn('Could not load resources:', e.message);
    }
  }

  function populateSelectOptions(resList) {
    const filter = document.getElementById('resourceFilter');
    const modal = document.getElementById('modalResource');
    if (!filter || !modal) return;

    filter.innerHTML = '<option value="">All Resources</option>';
    modal.innerHTML = '<option value="">Select Resource...</option>';

    resList.forEach(r => {
      filter.appendChild(new Option(r.name, r.id));
      modal.appendChild(new Option(r.name, r.id));
    });
  }

  function renderResourceCards(resList) {
    const container = document.getElementById('resourceCardsContainer');
    if (!container) return;

    if (!resList || resList.length === 0) {
      container.innerHTML = `<div class="col-12 text-center text-secondary py-4 small">No resources available.</div>`;
      return;
    }

    container.innerHTML = resList.map(r => {
      const categoryName = r.category_name || (r.category ? r.category.name : 'General');
      const amenitiesHtml = (r.amenities || []).map(a => `<span class="badge bg-light text-dark border me-1">${a}</span>`).join('');

      return `
        <div class="col-md-6 col-lg-3">
          <div class="card h-100 p-3 d-flex flex-column justify-content-between">
            <div>
              <div class="d-flex justify-content-between align-items-start mb-2">
                <h6 class="fw-bold mb-0 text-truncate" title="${r.name}">${r.name}</h6>
                <span class="badge bg-secondary-subtle text-secondary small">${categoryName}</span>
              </div>

              <p class="text-secondary small mb-2"><i class="bi bi-geo-alt me-1"></i>${r.location || 'Main Office'}</p>
              <p class="small text-muted mb-3" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                ${r.description || 'Available resource for scheduling.'}
              </p>

              <div class="d-flex justify-content-between text-secondary small mb-2 pt-2 border-top">
                <span><i class="bi bi-people me-1"></i>Capacity: ${r.capacity || 1}</span>
                <span><i class="bi bi-clock-history me-1"></i>Buffer: ${r.buffer_minutes || 15}m</span>
              </div>

              <div class="mb-3">
                ${amenitiesHtml}
              </div>
            </div>

            <button class="btn btn-outline-primary btn-sm w-100 open-book-modal" data-resource-id="${r.id}">
              <i class="bi bi-calendar-plus me-1"></i> Book Space
            </button>
          </div>
        </div>
      `;
    }).join('');

    document.querySelectorAll('.open-book-modal').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const resId = e.currentTarget.getAttribute('data-resource-id');
        openBookingModalForResource(resId);
      });
    });
  }

  function openBookingModalForResource(resourceId) {
    const modalEl = document.getElementById('bookingModal');
    if (!modalEl) return;
    const form = document.getElementById('bookingForm');
    if (form) {
      form.resource_id.value = resourceId;
      const start = new Date();
      start.setHours(start.getHours() + 1, 0, 0, 0);
      const end = new Date(start);
      end.setHours(end.getHours() + 1);

      form.start_datetime.value = toLocalInput(start);
      form.end_datetime.value = toLocalInput(end);
    }
    new bootstrap.Modal(modalEl).show();
  }

  function initCalendar() {
    const el = document.getElementById('calendar');
    if (!el) return;

    calendar = new FullCalendar.Calendar(el, {
      initialView: 'timeGridWeek',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay',
      },
      height: 'auto',
      slotMinTime: '08:00:00',
      slotMaxTime: '20:00:00',
      allDaySlot: false,
      nowIndicator: true,
      selectable: true,
      selectMirror: true,
      events: async (info, success, failure) => {
        try {
          let url = `/api/bookings/calendar/?start=${info.startStr}&end=${info.endStr}`;
          const resId = document.getElementById('resourceFilter')?.value;
          if (resId) url += `&resource=${resId}`;
          const events = await api(url);
          success(events);
        } catch (e) {
          console.error(e);
          success([]);
        }
      },
      select: (info) => {
        const modal = document.getElementById('bookingModal');
        if (!modal) return;
        const form = document.getElementById('bookingForm');
        form.start_datetime.value = toLocalInput(info.start);
        form.end_datetime.value = toLocalInput(info.end);
        new bootstrap.Modal(modal).show();
      },
      eventClick: (info) => {
        const p = info.event.extendedProps;
        alert(
          `Booking: ${info.event.title}\n` +
          `Status: ${p.status || 'Confirmed'}\n` +
          `Booked by: ${p.user || 'User'}\n` +
          (p.description ? `Notes: ${p.description}` : '')
        );
      },
    });
    calendar.render();

    document.getElementById('resourceFilter')?.addEventListener('change', () => {
      calendar.refetchEvents();
    });

    document.getElementById('searchResourceInput')?.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      const filtered = resources.filter(r =>
        r.name.toLowerCase().includes(q) ||
        (r.location && r.location.toLowerCase().includes(q)) ||
        (r.description && r.description.toLowerCase().includes(q))
      );
      renderResourceCards(filtered);
    });
  }

  function toLocalInput(d) {
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function fromLocalInput(s) {
    return new Date(s).toISOString();
  }

  document.getElementById('submitBooking')?.addEventListener('click', async () => {
    const form = document.getElementById('bookingForm');
    const errBox = document.getElementById('bookingError');
    if (!form) return;

    errBox.classList.add('d-none');
    const resId = parseInt(form.resource_id.value, 10);
    if (!resId) {
      errBox.textContent = 'Please select a resource.';
      errBox.classList.remove('d-none');
      return;
    }

    const payload = {
      resource_id: resId,
      title: form.title.value,
      description: form.description.value,
      start_datetime: fromLocalInput(form.start_datetime.value),
      end_datetime: fromLocalInput(form.end_datetime.value),
      attendees: parseInt(form.attendees.value, 10) || 1,
    };

    try {
      await api('/api/bookings/', { method: 'POST', body: JSON.stringify(payload) });
      const modalInstance = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));
      if (modalInstance) modalInstance.hide();
      form.reset();
      if (calendar) calendar.refetchEvents();
      alert('Reservation created successfully!');
    } catch (e) {
      errBox.textContent = e.message;
      errBox.classList.remove('d-none');
    }
  });

  document.addEventListener('DOMContentLoaded', () => {
    loadResources().then(initCalendar);
  });
})();
