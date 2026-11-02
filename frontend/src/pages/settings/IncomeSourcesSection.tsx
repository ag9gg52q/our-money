import { useEffect, useState } from 'react'

import { type IncomeSource, fetchIncomeSources } from '../../api/income_sources'
import Button from '../../components/Button/Button'
import IncomeSourceModal from '../../income_sources/IncomeSourceModal'
import styles from './CategoriesSection.module.css'

type LoadState = 'loading' | 'ready' | 'error'

export default function IncomeSourcesSection() {
  const [incomeSources, setIncomeSources] = useState<IncomeSource[]>([])
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [editing, setEditing] = useState<IncomeSource | 'new' | null>(null)

  useEffect(() => {
    let ignore = false

    fetchIncomeSources()
      .then((list) => {
        if (ignore) return
        setIncomeSources(list)
        if (!ignore) setLoadState('ready')
      })
      .catch(() => {
        if (!ignore) setLoadState('error')
      })

    return () => {
      ignore = true
    }
  }, [])

  function handleSaved(saved: IncomeSource) {
    setIncomeSources((prev) =>
      [...prev.filter((c) => c.id !== saved.id), saved].sort((a, b) =>
        a.name.localeCompare(b.name, 'ro'),
      ),
    )
    setEditing(null)
  }

  return (
    <section className={styles.card}>
      <div className={styles.header}>
        <div className={styles.heading}>
          <h2 className={styles.title}>Surse de Venit</h2>
          <p className={styles.description}>
            Folosite la înregistrarea veniturilor. O sursă de venit dezactivată
            nu mai apare în formulare.
          </p>
        </div>
        <Button type="button" onClick={() => setEditing('new')}>
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            aria-hidden="true"
          >
            <path d="M12 5v14M5 12h14" />
          </svg>
          Adaugă sursă de venit
        </Button>
      </div>

      {loadState === 'loading' && (
        <p className={styles.message}>Se încarcă...</p>
      )}

      {loadState === 'error' && (
        <p className={styles.alert} role="alert">
          Nu am putut încărca sursele de venit. Reîncarcă pagina.
        </p>
      )}

      {loadState === 'ready' && incomeSources.length === 0 && (
        <p className={styles.empty}>
          Nu ai încă nicio sursă de venit. Adaug-o pe prima.
        </p>
      )}

      {loadState === 'ready' && incomeSources.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th scope="col">Denumire</th>
                <th scope="col">Stare</th>
                <th scope="col">
                  <span className={styles.srOnly}>Acțiuni</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {incomeSources.map((incomeSource) => (
                <tr key={incomeSource.id}>
                  <td
                    className={
                      incomeSource.is_active ? styles.name : styles.nameInactive
                    }
                  >
                    {incomeSource.name}
                  </td>
                  <td>
                    {incomeSource.is_active ? (
                      <span className={styles.statusOn}>● Activă</span>
                    ) : (
                      <span className={styles.statusOff}>○ Dezactivată</span>
                    )}
                  </td>
                  <td className={styles.actionsCell}>
                    <button
                      type="button"
                      className={styles.iconButton}
                      aria-label={`Editează ${incomeSource.name}`}
                      onClick={() => setEditing(incomeSource)}
                    >
                      <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        aria-hidden="true"
                      >
                        <path d="M4 20h4L19 9l-4-4L4 16z" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {editing !== null && (
        <IncomeSourceModal
          incomeSource={editing === 'new' ? undefined : editing}
          onClose={() => setEditing(null)}
          onSaved={handleSaved}
        />
      )}
    </section>
  )
}
