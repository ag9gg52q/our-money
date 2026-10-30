import { useEffect, useState } from 'react'
import { Link } from 'react-router'

import { type Category, fetchCategories } from '../../api/categories'
import { type Subcategory, fetchSubcategories } from '../../api/subcategories'
import Button from '../../components/Button/Button'
import Select from '../../components/Select/Select'
import SubcategoryModal from '../../subcategories/SubcategoryModal'
import styles from './CategoriesSection.module.css'
import pickerStyles from './SubcategoriesSection.module.css'

type LoadState = 'loading' | 'ready' | 'error'

export default function SubcategoriesSection() {
  const [categories, setCategories] = useState<Category[]>([])
  const [categoriesState, setCategoriesState] = useState<LoadState>('loading')
  const [categoryId, setCategoryId] = useState('')
  const [subcategories, setSubcategories] = useState<Subcategory[]>([])
  const [subcategoriesState, setSubcategoriesState] =
    useState<LoadState>('loading')
  const [editing, setEditing] = useState<Subcategory | 'new' | null>(null)

  useEffect(() => {
    let ignore = false

    fetchCategories()
      .then((list) => {
        if (ignore) return
        const active = list.filter((c) => c.is_active)
        setCategories(active)
        setCategoryId(active[0]?.id ?? '')
        setCategoriesState('ready')
      })
      .catch(() => {
        if (!ignore) setCategoriesState('error')
      })

    return () => {
      ignore = true
    }
  }, [])

  useEffect(() => {
    if (categoryId === '') return
    let ignore = false

    fetchSubcategories(categoryId)
      .then((list) => {
        if (ignore) return
        setSubcategories(list)
        setSubcategoriesState('ready')
      })
      .catch(() => {
        if (!ignore) setSubcategoriesState('error')
      })

    return () => {
      ignore = true
    }
  }, [categoryId])

  function handleCategoryChange(value: string) {
    if (value === categoryId) return
    setCategoryId(value)
    setSubcategoriesState('loading')
  }

  function handleSaved(saved: Subcategory) {
    setSubcategories((prev) =>
      [...prev.filter((s) => s.id !== saved.id), saved].sort((a, b) =>
        a.name.localeCompare(b.name, 'ro'),
      ),
    )
    setEditing(null)
  }

  return (
    <section className={styles.card}>
      <div className={styles.header}>
        <div className={styles.heading}>
          <h2 className={styles.title}>Subcategorii</h2>
          <p className={styles.description}>
            Detaliază fiecare categorie de cheltuieli. O subcategorie
            dezactivată nu mai apare în formulare.
          </p>
        </div>
      </div>

      {categoriesState === 'loading' && (
        <p className={styles.message}>Se încarcă...</p>
      )}

      {categoriesState === 'error' && (
        <p className={styles.alert} role="alert">
          Nu am putut încărca categoriile. Reîncarcă pagina.
        </p>
      )}

      {categoriesState === 'ready' && categories.length === 0 && (
        <p className={styles.empty}>
          Nu ai încă nicio categorie activă. Adaug-o mai întâi în{' '}
          <Link to="../categorii" relative="path" className={pickerStyles.link}>
            Categorii
          </Link>
          .
        </p>
      )}

      {categoriesState === 'ready' && categories.length > 0 && (
        <>
          <div className={pickerStyles.toolbar}>
            <div className={pickerStyles.picker}>
              <Select
                label="Categoria"
                value={categoryId}
                options={categories.map((category) => ({
                  value: category.id,
                  label: category.name,
                }))}
                onChange={handleCategoryChange}
              />
            </div>
            <Button
              type="button"
              className={pickerStyles.addButton}
              onClick={() => setEditing('new')}
            >
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
              Adaugă subcategorie
            </Button>
          </div>

          {subcategoriesState === 'loading' && (
            <p className={styles.message}>Se încarcă...</p>
          )}

          {subcategoriesState === 'error' && (
            <p className={styles.alert} role="alert">
              Nu am putut încărca subcategoriile. Reîncarcă pagina.
            </p>
          )}

          {subcategoriesState === 'ready' && subcategories.length === 0 && (
            <p className={styles.empty}>
              Categoria aleasă nu are încă subcategorii. Adaug-o pe prima.
            </p>
          )}

          {subcategoriesState === 'ready' && subcategories.length > 0 && (
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
                  {subcategories.map((subcategory) => (
                    <tr key={subcategory.id}>
                      <td
                        className={
                          subcategory.is_active
                            ? styles.name
                            : styles.nameInactive
                        }
                      >
                        {subcategory.name}
                      </td>
                      <td>
                        {subcategory.is_active ? (
                          <span className={styles.statusOn}>● Activă</span>
                        ) : (
                          <span className={styles.statusOff}>
                            ○ Dezactivată
                          </span>
                        )}
                      </td>
                      <td className={styles.actionsCell}>
                        <button
                          type="button"
                          className={styles.iconButton}
                          aria-label={`Editează ${subcategory.name}`}
                          onClick={() => setEditing(subcategory)}
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
        </>
      )}

      {editing !== null && (
        <SubcategoryModal
          categoryId={categoryId}
          subcategory={editing === 'new' ? undefined : editing}
          onClose={() => setEditing(null)}
          onSaved={handleSaved}
        />
      )}
    </section>
  )
}
