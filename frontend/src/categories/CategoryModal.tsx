import { type SubmitEvent, useState } from 'react'

import {
  type Category,
  createCategory,
  updateCategory,
} from '../api/categories'
import { getErrorMessage } from '../api/client'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import TextField from '../components/TextField/TextField'
import styles from './CategoryModal.module.css'

type CategoryModalProps = {
  category?: Category
  onClose: () => void
  onSaved: (category: Category) => void
}

export default function CategoryModal({
  category,
  onClose,
  onSaved,
}: CategoryModalProps) {
  const isEdit = category !== undefined

  const [name, setName] = useState(category?.name ?? '')
  const [isActive, setIsActive] = useState(category?.is_active ?? true)
  const [error, setError] = useState<unknown>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleClose() {
    if (!isSubmitting) onClose()
  }

  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      const saved = category
        ? await updateCategory(category.id, { name, is_active: isActive })
        : await createCategory(name)
      onSaved(saved)
    } catch (caught) {
      setError(caught)
      setIsSubmitting(false)
    }
  }

  const nameError = getErrorMessage(error, 'name')
  const formError =
    error && !nameError
      ? (getErrorMessage(error, 'non_field_errors') ??
        getErrorMessage(error, 'detail') ??
        'Nu ne-am putut conecta la server. Încearcă din nou.')
      : undefined

  return (
    <Modal
      title={isEdit ? 'Editează categoria' : 'Adaugă categorie'}
      onClose={handleClose}
    >
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {formError && (
          <p className={styles.alert} role="alert">
            {formError}
          </p>
        )}
        <TextField
          label="Denumire"
          maxLength={50}
          autoFocus
          value={name}
          onChange={(event) => setName(event.target.value)}
          error={nameError}
        />
        {isEdit && (
          <label className={styles.checkbox}>
            <input
              type="checkbox"
              checked={isActive}
              onChange={(event) => setIsActive(event.target.checked)}
            />
            Activă
            <span className={styles.hint}>
              O categorie dezactivată nu mai apare în formulare.
            </span>
          </label>
        )}
        <div className={styles.actions}>
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Anulează
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Se salvează...' : 'Salvează'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
