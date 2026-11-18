import styles from './Avatar.module.css'

type AvatarProps = {
  name: string
  imageUrl?: string
}

const COLORS = ['accent', 'info', 'warm'] as const

function colorFor(name: string) {
  let sum = 0
  for (const ch of name) sum += ch.codePointAt(0) ?? 0
  return COLORS[sum % COLORS.length]
}

export default function Avatar({ name, imageUrl }: AvatarProps) {
  const initial = name.charAt(0).toUpperCase()

  return (
    <span
      className={`${styles.avatar} ${styles[colorFor(name)]}`}
      role="img"
      aria-label={name}
    >
      {imageUrl ? (
        <img className={styles.image} src={imageUrl} alt="" />
      ) : (
        <span aria-hidden="true">{initial}</span>
      )}
      <span className={styles.tooltip} aria-hidden="true">
        {name}
      </span>
    </span>
  )
}
