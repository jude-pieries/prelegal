export type MndaTermType = 'expires' | 'continues'
export type ConfidentialityTermType = 'years' | 'perpetuity'

export interface MndaFormData {
  purpose: string
  effectiveDate: string
  mndaTermType: MndaTermType
  mndaTermYears: number
  confidentialityTermType: ConfidentialityTermType
  confidentialityTermYears: number
  governingLaw: string
  jurisdiction: string
  party1Name: string
  party1Title: string
  party1Company: string
  party1NoticeAddress: string
  party2Name: string
  party2Title: string
  party2Company: string
  party2NoticeAddress: string
}

export const defaultMndaFormData: MndaFormData = {
  purpose: 'Evaluating whether to enter into a business relationship with the other party.',
  effectiveDate: new Date().toISOString().split('T')[0],
  mndaTermType: 'expires',
  mndaTermYears: 1,
  confidentialityTermType: 'years',
  confidentialityTermYears: 1,
  governingLaw: '',
  jurisdiction: '',
  party1Name: '',
  party1Title: '',
  party1Company: '',
  party1NoticeAddress: '',
  party2Name: '',
  party2Title: '',
  party2Company: '',
  party2NoticeAddress: '',
}
