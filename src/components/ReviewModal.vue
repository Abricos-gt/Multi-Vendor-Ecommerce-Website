<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Rate This Product</h3>
        <button class="modal-close" @click="handleClose">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="review-form">
        <div class="form-group">
          <label>Rating *</label>
          <div class="rating-input">
            <button
              type="button"
              class="star-btn"
              :class="{ active: 1 <= rating }"
              @click="rating = 1"
            >
              <i class="fas fa-star"></i>
            </button>
            <button
              type="button"
              class="star-btn"
              :class="{ active: 2 <= rating }"
              @click="rating = 2"
            >
              <i class="fas fa-star"></i>
            </button>
            <button
              type="button"
              class="star-btn"
              :class="{ active: 3 <= rating }"
              @click="rating = 3"
            >
              <i class="fas fa-star"></i>
            </button>
            <button
              type="button"
              class="star-btn"
              :class="{ active: 4 <= rating }"
              @click="rating = 4"
            >
              <i class="fas fa-star"></i>
            </button>
            <button
              type="button"
              class="star-btn"
              :class="{ active: 5 <= rating }"
              @click="rating = 5"
            >
              <i class="fas fa-star"></i>
            </button>
            <span class="rating-text">{{ rating }}/5 stars</span>
          </div>
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn-secondary" @click="handleClose">
            Cancel
          </button>
          <button type="submit" class="btn-primary" :disabled="!rating || submitting">
            <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-star"></i>
            {{ submitting ? 'Submitting...' : 'Submit Rating' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReviewModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    submitting: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      rating: 0,
      comment: ''
    }
  },
  watch: {
    show: {
      handler(newVal) {
        if (!newVal) {
          this.resetForm()
        }
      },
      immediate: true
    }
  },
  methods: {
    resetForm() {
      this.rating = 0
      this.comment = ''
    },
    handleClose() {
      this.$emit('close')
    },
    handleSubmit() {
      if (!this.rating) return
      
      this.$emit('submit', {
        rating: this.rating,
        comment: '' // No comment needed
      })
    }
  }
}
</script>

<style scoped>
/* Review Form Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-content {
  background: var(--card-bg, #ffffff);
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  margin-bottom: 24px;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary, #0f172a);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  color: var(--text-secondary, #6b7280);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: var(--bg-secondary, #f8fafc);
  color: var(--text-primary, #0f172a);
}

.review-form {
  padding: 0 24px 24px;
}

.review-form .form-group {
  margin-bottom: 24px;
}

.review-form label {
  display: block;
  font-weight: 500;
  color: var(--text-primary, #0f172a);
  margin-bottom: 8px;
}

.rating-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #d1d5db;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.star-btn:hover,
.star-btn.active {
  color: #f59e0b;
  transform: scale(1.1);
}

.rating-text {
  margin-left: 12px;
  font-size: 14px;
  color: var(--text-secondary, #6b7280);
  font-weight: 500;
}

.review-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  min-height: 100px;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.review-form textarea:focus {
  outline: none;
  border-color: var(--accent-color, #37A000);
  box-shadow: 0 0 0 2px rgba(55, 160, 0, 0.25);
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.form-actions button {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.form-actions .btn-secondary {
  background: var(--bg-secondary, #f8fafc);
  color: var(--text-primary, #0f172a);
  border-color: var(--border-color, #e5e7eb);
}

.form-actions .btn-secondary:hover {
  background: var(--border-color, #e5e7eb);
}

.form-actions .btn-primary {
  background: var(--accent-color, #37A000);
  color: #ffffff;
}

.form-actions .btn-primary:hover:not(:disabled) {
  background: #2d7a00;
}

.form-actions .btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
