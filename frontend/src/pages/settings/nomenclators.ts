export type Nomenclator = {
  path: string
  label: string
  description: string
}

export const NOMENCLATORS: Nomenclator[] = [
  {
    path: 'categorii',
    label: 'Categorii',
    description: 'Folosite la înregistrarea cheltuielilor.',
  },
  {
    path: 'subcategorii',
    label: 'Subcategorii',
    description: 'Detaliază fiecare categorie de cheltuieli.',
  },
  {
    path: 'surse-venit',
    label: 'Surse de venit',
    description: 'Folosite la înregistrarea veniturilor.',
  },
  {
    path: 'gospodarie',
    label: 'Gospodărie',
    description: 'Numele gospodăriei, codul de invitație și persoanele din ea.',
  },
]
