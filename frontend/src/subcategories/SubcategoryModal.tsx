import { type SubmitEvent, useState } from 'react'

import {
  type Subcategory,
  createSubcategory,
  updateSubcategory,
} from '../api/subcategories'
import { getErrorMessage } from '../api/client'
import Button from '../components/Button/Button'
import Modal from '../components/Modal/Modal'
import TextField from '../components/TextField/TextField'
import styles from '../categories/CategoryModal.module.css'

type SubcategoryModalProps = {
  categoryId: string
  subcategory?: Subcategory
  onClose: () => void
  onSaved: (subcategory: Subcategory) => void
}

export default function SubcategoryModal({
  categoryId,
  subcategory,
  onClose,
  onSaved,
}: SubcategoryModalProps) {
  const isEdit = subcategory !== undefined

  const [name, setName] = useState(subcategory?.name ?? '')
  const [isActive, setIsActive] = useState(subcategory?.is_active ?? true)
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
      const saved = subcategory
        ? await updateSubcategory(subcategory.id, { name, is_active: isActive })
        : await createSubcategory(categoryId, name)
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
      title={isEdit ? 'Editează subcategoria' : 'Adaugă subcategorie'}
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
              O subcategorie dezactivată nu mai apare în formulare.
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
