import type { ReactNode } from 'react'

import styles from './AuthLayout.module.css'

type AuthLayoutProps = {
  title: string
  subtitle: string
  children: ReactNode
  footer: ReactNode
}

export default function AuthLayout({
  title,
  subtitle,
  children,
  footer,
}: AuthLayoutProps) {
  return (
    <div className={styles.page}>
      <section className={styles.brand}>
        <div className={styles.logo}>
          <span className={styles.logoMark}>OM</span>
          Our Money
        </div>
        <div className={styles.tagline}>
          <h1 className={styles.taglineTitle}>
            Banii familiei, într-un singur loc.
          </h1>
          <p className={styles.taglineText}>
            Cheltuieli, venituri și rapoarte — fără foi de calcul.
          </p>
        </div>
        <p className={styles.copyright}>© 2026 Our Money</p>
      </section>

      <main className={styles.main}>
        <div className={styles.panel}>
          <div className={styles.heading}>
            <h2 className={styles.title}>{title}</h2>
            <p className={styles.subtitle}>{subtitle}</p>
          </div>
          {children}
          <p className={styles.footer}>{footer}</p>
        </div>
      </main>
    </div>
  )
}
