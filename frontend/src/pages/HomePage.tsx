import type { ReactNode } from 'react'
import { Link } from 'react-router'

import { useAuth } from '../auth/useAuth'
import Button from '../components/Button/Button'
import styles from './HomePage.module.css'

type QuickAction = {
  title: string
  description: string
  icon: ReactNode
  tone: 'accent' | 'info' | 'warm'
  to?: string
}

function Icon({ children }: { children: ReactNode }) {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  )
}

export default function HomePage() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const today = new Date().toLocaleDateString('ro-RO', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  })

  const actions: QuickAction[] = [
    {
      title: 'Adaugă cheltuială',
      description: 'Completează manual sau pornește de la un template.',
      icon: (
        <Icon>
          <path d="M12 5v14M5 12h14" />
        </Icon>
      ),
      tone: 'accent',
    },
    {
      title: 'Adaugă venit',
      description: 'Salariu, bonus sau alte intrări de bani.',
      icon: (
        <Icon>
          <path d="M17 7 7 17M15 17H7V9" />
        </Icon>
      ),
      tone: 'info',
    },
  ]
  if (isAdmin) {
    actions.push({
      title: 'Setări sistem',
      description: 'Nomenclatoare, template-uri și rapoarte.',
      icon: (
        <Icon>
          <path d="M4 7h9M17 7h3M4 12h3M11 12h9M4 17h11M19 17h1" />
          <circle cx="15" cy="7" r="2" />
          <circle cx="9" cy="12" r="2" />
          <circle cx="17" cy="17" r="2" />
        </Icon>
      ),
      tone: 'warm',
      to: '/settings',
    })
  }

  return (
    <div className={styles.page}>
      <section className={styles.intro}>
        <p className={styles.date}>{today}</p>
        <h1 className={styles.title}>Bună ziua, {user?.username}</h1>
        <p className={styles.lead}>
          {isAdmin
            ? 'Ține evidența cheltuielilor și veniturilor într-un singur loc. Începe cu o acțiune rapidă de mai jos.'
            : 'Ce ai cheltuit sau încasat azi? Adaugă în câteva secunde.'}
        </p>
      </section>

      <section className={styles.actions} aria-label="Acțiuni rapide">
        {actions.map((action) => {
          const content = (
            <>
              <span className={`${styles.icon} ${styles[action.tone]}`}>
                {action.icon}
              </span>
              <span className={styles.cardTitle}>{action.title}</span>
              <span className={styles.cardText}>{action.description}</span>
            </>
          )
          return action.to ? (
            <Link key={action.title} to={action.to} className={styles.card}>
              {content}
            </Link>
          ) : (
            <div
              key={action.title}
              className={`${styles.card} ${styles.disabled}`}
              aria-disabled="true"
            >
              {content}
              <span className={styles.soon}>În curând</span>
            </div>
          )
        })}
      </section>

      <section className={styles.empty} aria-label="Rapoarte">
        <svg
          width="36"
          height="36"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M5 20V11M11 20V5M17 20v-7M3 20h18" />
        </svg>
        <h2 className={styles.emptyTitle}>
          {isAdmin
            ? 'Aici vor apărea rapoartele tale'
            : 'Încă nu sunt rapoarte'}
        </h2>
        <p className={styles.emptyText}>
          {isAdmin
            ? 'Creează un raport în Setări sistem și fixează-l pe pagina de start.'
            : 'Rapoartele create de administrator vor apărea aici.'}
        </p>
        {isAdmin && (
          <Button type="button" variant="secondary" disabled>
            Creează un raport
          </Button>
        )}
      </section>
    </div>
  )
}
