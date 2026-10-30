import { type KeyboardEvent, useEffect, useId, useRef, useState } from 'react'

import styles from './Select.module.css'

export type SelectOption = {
  value: string
  label: string
}

type SelectProps = {
  label: string
  value: string
  options: SelectOption[]
  onChange: (value: string) => void
}

export default function Select({
  label,
  value,
  options,
  onChange,
}: SelectProps) {
  const id = useId()
  const buttonId = `${id}-button`
  const listId = `${id}-list`
  const optionId = (index: number) => `${id}-option-${index}`

  const rootRef = useRef<HTMLDivElement>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(0)

  const selectedIndex = options.findIndex((option) => option.value === value)
  const selected = options[selectedIndex]

  // Lista se închide la un click în afara componentei.
  useEffect(() => {
    if (!isOpen) return

    function handlePointerDown(event: PointerEvent) {
      if (!rootRef.current?.contains(event.target as Node)) setIsOpen(false)
    }

    document.addEventListener('pointerdown', handlePointerDown)
    return () => document.removeEventListener('pointerdown', handlePointerDown)
  }, [isOpen])

  // Opțiunea activă rămâne vizibilă când lista are scroll.
  useEffect(() => {
    if (!isOpen) return
    document
      .getElementById(optionId(activeIndex))
      ?.scrollIntoView({ block: 'nearest' })
  })

  function open() {
    setActiveIndex(Math.max(selectedIndex, 0))
    setIsOpen(true)
  }

  function choose(index: number) {
    onChange(options[index].value)
    setIsOpen(false)
  }

  function handleKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    if (!isOpen) {
      if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(event.key)) {
        event.preventDefault()
        open()
      }
      return
    }

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        setActiveIndex((index) => Math.min(index + 1, options.length - 1))
        break
      case 'ArrowUp':
        event.preventDefault()
        setActiveIndex((index) => Math.max(index - 1, 0))
        break
      case 'Home':
        event.preventDefault()
        setActiveIndex(0)
        break
      case 'End':
        event.preventDefault()
        setActiveIndex(options.length - 1)
        break
      case 'Enter':
      case ' ':
        event.preventDefault()
        choose(activeIndex)
        break
      case 'Escape':
        event.preventDefault()
        setIsOpen(false)
        break
      case 'Tab':
        setIsOpen(false)
        break
    }
  }

  return (
    <div className={styles.field} ref={rootRef}>
      <label htmlFor={buttonId} className={styles.label}>
        {label}
      </label>
      <div className={styles.control}>
        <button
          id={buttonId}
          type="button"
          role="combobox"
          className={styles.trigger}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          aria-controls={listId}
          aria-activedescendant={isOpen ? optionId(activeIndex) : undefined}
          onClick={() => (isOpen ? setIsOpen(false) : open())}
          onKeyDown={handleKeyDown}
        >
          <span className={styles.value}>{selected?.label ?? 'Alege...'}</span>
          <svg
            className={styles.chevron}
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="m6 9 6 6 6-6" />
          </svg>
        </button>

        {isOpen && (
          <ul
            id={listId}
            role="listbox"
            className={styles.list}
            aria-labelledby={buttonId}
            // Focusul rămâne pe buton când se apasă pe o opțiune.
            onMouseDown={(event) => event.preventDefault()}
          >
            {options.map((option, index) => (
              <li
                key={option.value}
                id={optionId(index)}
                role="option"
                aria-selected={index === selectedIndex}
                className={[
                  styles.option,
                  index === activeIndex && styles.active,
                  index === selectedIndex && styles.selected,
                ]
                  .filter(Boolean)
                  .join(' ')}
                onMouseEnter={() => setActiveIndex(index)}
                onClick={() => choose(index)}
              >
                <span>{option.label}</span>
                {index === selectedIndex && (
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.4"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M5 12.5 10 17.5 19 7" />
                  </svg>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
