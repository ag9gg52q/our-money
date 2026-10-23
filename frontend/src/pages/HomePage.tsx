import { useAuth } from '../auth/useAuth'

// Schiță: pagina gospodăriei va fi dezvoltată ulterior.
export default function HomePage() {
  const { user } = useAuth()

  return (
    <>
      <h1>Gospodăria noastră</h1>
      <p>Bun venit, {user?.username}! Aici vor apărea datele gospodăriei.</p>
    </>
  )
}
