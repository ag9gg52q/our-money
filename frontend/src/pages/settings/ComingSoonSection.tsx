import styles from './ComingSoonSection.module.css'

type ComingSoonSectionProps = {
  title: string
  description: string
}

export default function ComingSoonSection({
  title,
  description,
}: ComingSoonSectionProps) {
  return (
    <section className={styles.card}>
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.description}>{description}</p>
      <p className={styles.soon}>În curând</p>
    </section>
  )
}
