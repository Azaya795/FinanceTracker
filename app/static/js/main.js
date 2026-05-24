/**
 * SWE 2026 Course Template - Client-Side Controller
 * Handles interactive AJAX/fetch CRUD calls with Flask API endpoints securely.
 */

document.addEventListener('DOMContentLoaded', () => {
  const taskForm = document.getElementById('taskForm');
  const taskList = document.getElementById('taskList');
  const taskCounter = document.getElementById('taskCounter');
  const loadingState = document.getElementById('loadingState');
  const emptyState = document.getElementById('emptyState');
  
  // Load tasks on init
  fetchTasks();

  // Form Submit Handler (Create Operation)
  taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const titleInput = document.getElementById('title');
    const descInput = document.getElementById('description');
    
    const title = titleInput.value.trim();
    const description = descInput.value.trim();
    
    if (!title) return;
    
    // Disable submit button during fetch
    const submitBtn = taskForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.7';
    
    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        // Clear input fields
        titleInput.value = '';
        descInput.value = '';
        // Reload list
        await fetchTasks();
      } else {
        alert(`Error: ${result.error || 'Failed to create entry'}`);
      }
    } catch (err) {
      console.error('Error creating task:', err);
      alert('Network error. Failed to reach the Flask API backend.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.style.opacity = '1';
    }
  });

  // Fetch Tasks List (Read Operation)
  async function fetchTasks() {
    showState('loading');
    
    try {
      const response = await fetch('/api/tasks');
      if (!response.ok) throw new Error('Failed to fetch tasks');
      
      const tasks = await response.json();
      renderTasks(tasks);
    } catch (err) {
      console.error('Error loading tasks:', err);
      showState('empty'); // Fallback to empty state with error notice
    }
  }

  // Render Tasks dynamically to DOM
  def_date_format = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return dateStr;
    }
  };

  function renderTasks(tasks) {
    // Update counter
    taskCounter.textContent = `${tasks.length} Entr${tasks.length === 1 ? 'y' : 'ies'}`;
    
    if (tasks.length === 0) {
      showState('empty');
      return;
    }
    
    taskList.innerHTML = '';
    
    tasks.forEach(task => {
      const li = document.createElement('li');
      li.className = `task-item ${task.status === 'done' ? 'done' : ''}`;
      
      li.innerHTML = `
        <div class="task-item-content">
          <label class="checkbox-container">
            <input type="checkbox" ${task.status === 'done' ? 'checked' : ''} onchange="toggleTaskStatus(${task.id})">
            <span class="checkmark"></span>
          </label>
          <div class="task-details">
            <h4>${escapeHTML(task.title)}</h4>
            ${task.description ? `<p>${escapeHTML(task.description)}</p>` : ''}
            <div class="task-meta">
              <span class="task-date"><i class="fa-regular fa-clock"></i> ${def_date_format(task.created_at)}</span>
              <span class="task-tag">${task.status === 'done' ? 'Completed' : 'Pending'}</span>
            </div>
          </div>
        </div>
        <button class="btn-delete" onclick="deleteTaskEntry(${task.id})" title="Delete Entry">
          <i class="fa-regular fa-trash-can"></i>
        </button>
      `;
      
      taskList.appendChild(li);
    });
    
    showState('list');
  }

  // Toggle Status Helper (Update Operation)
  window.toggleTaskStatus = async (id) => {
    try {
      const response = await fetch(`/api/tasks/${id}/toggle`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchTasks();
      } else {
        const result = await response.json();
        alert(`Error: ${result.error || 'Failed to toggle status'}`);
      }
    } catch (err) {
      console.error('Error toggling task:', err);
    }
  };

  // Delete Entry Helper (Delete Operation)
  window.deleteTaskEntry = async (id) => {
    if (!confirm('Are you sure you want to delete this entry?')) return;
    
    try {
      const response = await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchTasks();
      } else {
        const result = await response.json();
        alert(`Error: ${result.error || 'Failed to delete entry'}`);
      }
    } catch (err) {
      console.error('Error deleting task:', err);
    }
  };

  // Helper to switch view states cleanly
  function showState(state) {
    loadingState.classList.add('hidden');
    emptyState.classList.add('hidden');
    taskList.classList.add('hidden');
    
    if (state === 'loading') {
      loadingState.classList.remove('hidden');
    } else if (state === 'empty') {
      emptyState.classList.remove('hidden');
    } else if (state === 'list') {
      taskList.classList.remove('hidden');
    }
  }

  // XSS Prevention helper
  function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
      tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
      }[tag] || tag)
    );
  }
});
