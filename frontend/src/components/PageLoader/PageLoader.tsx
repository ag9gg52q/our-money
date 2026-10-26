import styles from './PageLoader.module.css'

export default function PageLoader() {
  return (
    <div className={styles.loader} role="status">
      Se încarcă...
    </div>
  )
}
