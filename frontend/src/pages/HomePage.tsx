import { useAuth } from '../auth/useAuth'

export default function HomePage() {
  const { user } = useAuth()

  return (
    <>
      <h1>Bun venit, {user?.username}!</h1>
      <p>Aici va fi bugetul nostru.</p>
    </>
  )
}
