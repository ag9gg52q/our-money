import { type ReactNode, useEffect, useId, useRef } from 'react'

import styles from './Modal.module.css'

type ModalProps = {
  title: string
  onClose: () => void
  children: ReactNode
  size?: 'default' | 'wide'
}

export default function Modal({
  title,
  onClose,
  children,
  size = 'default',
}: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const titleId = useId()

  useEffect(() => {
    const dialog = dialogRef.current
    dialog?.showModal()
    // showModal() pune focusul pe primul câmp; un câmp marcat cu data-autofocus îl preia.
    dialog?.querySelector<HTMLElement>('[data-autofocus]')?.focus()
    return () => dialog?.close()
  }, [])

  return (
    <dialog
      ref={dialogRef}
      className={`${styles.dialog} ${size === 'wide' ? styles.wide : ''}`}
      aria-labelledby={titleId}
      onCancel={(event) => {
        // Un modal deschis peste acesta își tratează singur Escape-ul.
        if (event.target !== event.currentTarget) return
        event.preventDefault()
        onClose()
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div className={styles.body}>
        <h2 id={titleId} className={styles.title}>
          {title}
        </h2>
        {children}
      </div>
    </dialog>
  )
}
