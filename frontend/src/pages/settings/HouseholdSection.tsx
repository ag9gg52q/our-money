import { useEffect, useState } from 'react'

import {
  type HouseholdDetails,
  type HouseholdMember,
  fetchCurrentHousehold,
} from '../../api/households'
import Button from '../../components/Button/Button'
import styles from './CategoriesSection.module.css'
import householdStyles from './HouseholdSection.module.css'

type LoadState = 'loading' | 'ready' | 'error'

const ROLE_LABELS: Record<HouseholdMember['role'], string> = {
  admin: 'Administrator',
  user: 'Utilizator',
}

function fullName(member: HouseholdMember) {
  return [member.first_name, member.last_name].filter(Boolean).join(' ')
}

export default function HouseholdSection() {
  const [household, setHousehold] = useState<HouseholdDetails | null>(null)
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    let ignore = false

    fetchCurrentHousehold()
      .then((data) => {
        if (ignore) return
        setHousehold(data)
        setLoadState('ready')
      })
      .catch(() => {
        if (!ignore) setLoadState('error')
      })

    return () => {
      ignore = true
    }
  }, [])

  async function handleCopy() {
    if (!household?.invite_code) return
    await navigator.clipboard.writeText(household.invite_code)
    setCopied(true)
  }

  return (
    <section className={styles.card}>
      <div className={styles.header}>
        <div className={styles.heading}>
          <h2 className={styles.title}>{household?.name ?? 'Gospodărie'}</h2>
          <p className={styles.description}>
            Codul de invitație și persoanele din gospodărie.
          </p>
        </div>
      </div>

      {loadState === 'loading' && (
        <p className={styles.message}>Se încarcă...</p>
      )}

      {loadState === 'error' && (
        <p className={styles.alert} role="alert">
          Nu am putut încărca gospodăria. Reîncarcă pagina.
        </p>
      )}

      {household && (
        <>
          {household.invite_code && (
            <div className={householdStyles.block}>
              <h3 className={householdStyles.blockTitle}>Cod de invitație</h3>
              <p className={householdStyles.hint}>
                Trimite codul persoanelor pe care vrei să le adaugi în
                gospodărie.
              </p>
              <div className={householdStyles.codeRow}>
                <code className={householdStyles.code}>
                  {household.invite_code}
                </code>
                <Button type="button" variant="secondary" onClick={handleCopy}>
                  {copied ? 'Copiat' : 'Copiază'}
                </Button>
              </div>
            </div>
          )}

          <div className={householdStyles.block}>
            <h3 className={householdStyles.blockTitle}>Membri</h3>
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th scope="col">Utilizator</th>
                    <th scope="col">Rol</th>
                    <th scope="col">
                      <span className={styles.srOnly}>Acțiuni</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {household.members.map((member) => (
                    <tr key={member.id}>
                      <td>
                        <span className={styles.name}>{member.username}</span>
                        {fullName(member) && (
                          <span className={householdStyles.fullName}>
                            {fullName(member)}
                          </span>
                        )}
                      </td>
                      <td>
                        <span
                          className={
                            member.role === 'admin'
                              ? householdStyles.roleAdmin
                              : householdStyles.roleUser
                          }
                        >
                          {ROLE_LABELS[member.role]}
                        </span>
                      </td>
                      <td className={styles.actionsCell} />
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </section>
  )
}
