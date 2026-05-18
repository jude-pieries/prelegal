'use client'

import { type MndaFormData } from '@/lib/types'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'

interface MndaFormProps {
  data: MndaFormData
  onChange: (data: MndaFormData) => void
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4 pb-2 border-b">
      {children}
    </h2>
  )
}

function Field({
  label,
  hint,
  children,
}: {
  label: string
  hint?: string
  children: React.ReactNode
}) {
  return (
    <div className="space-y-1.5">
      <Label className="text-sm font-medium">{label}</Label>
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
      {children}
    </div>
  )
}

export function MndaForm({ data, onChange }: MndaFormProps) {
  function set<K extends keyof MndaFormData>(key: K, value: MndaFormData[K]) {
    onChange({ ...data, [key]: value })
  }

  return (
    <div className="space-y-8">
      <section>
        <SectionHeading>Agreement Details</SectionHeading>
        <div className="space-y-5">
          <Field label="Purpose" hint="How Confidential Information may be used">
            <Textarea
              value={data.purpose}
              onChange={(e) => set('purpose', e.target.value)}
              rows={3}
              placeholder="Describe the purpose of this NDA…"
            />
          </Field>
          <Field label="Effective Date">
            <Input
              type="date"
              value={data.effectiveDate}
              onChange={(e) => set('effectiveDate', e.target.value)}
            />
          </Field>
        </div>
      </section>

      <section>
        <SectionHeading>Agreement Terms</SectionHeading>
        <div className="space-y-6">
          <Field label="MNDA Term" hint="The length of this MNDA">
            <RadioGroup
              value={data.mndaTermType}
              onValueChange={(v) => set('mndaTermType', v as MndaFormData['mndaTermType'])}
              className="space-y-2"
            >
              <div className="flex items-center gap-2">
                <RadioGroupItem value="expires" id="term-expires" />
                <Label
                  htmlFor="term-expires"
                  className="flex items-center gap-2 cursor-pointer font-normal"
                >
                  Expires
                  <Input
                    type="number"
                    min={1}
                    max={99}
                    value={data.mndaTermYears}
                    onChange={(e) => set('mndaTermYears', Math.max(1, Number(e.target.value)))}
                    onFocus={() => set('mndaTermType', 'expires')}
                    className="w-16 h-7 px-2 text-center"
                  />
                  year(s) from Effective Date
                </Label>
              </div>
              <div className="flex items-center gap-2">
                <RadioGroupItem value="continues" id="term-continues" />
                <Label htmlFor="term-continues" className="cursor-pointer font-normal">
                  Continues until terminated
                </Label>
              </div>
            </RadioGroup>
          </Field>

          <Field label="Term of Confidentiality" hint="How long Confidential Information is protected">
            <RadioGroup
              value={data.confidentialityTermType}
              onValueChange={(v) =>
                set('confidentialityTermType', v as MndaFormData['confidentialityTermType'])
              }
              className="space-y-2"
            >
              <div className="flex items-center gap-2">
                <RadioGroupItem value="years" id="conf-years" />
                <Label
                  htmlFor="conf-years"
                  className="flex items-center gap-2 cursor-pointer font-normal"
                >
                  <Input
                    type="number"
                    min={1}
                    max={99}
                    value={data.confidentialityTermYears}
                    onChange={(e) =>
                      set('confidentialityTermYears', Math.max(1, Number(e.target.value)))
                    }
                    onFocus={() => set('confidentialityTermType', 'years')}
                    className="w-16 h-7 px-2 text-center"
                  />
                  year(s) from Effective Date
                </Label>
              </div>
              <div className="flex items-center gap-2">
                <RadioGroupItem value="perpetuity" id="conf-perpetuity" />
                <Label htmlFor="conf-perpetuity" className="cursor-pointer font-normal">
                  In perpetuity
                </Label>
              </div>
            </RadioGroup>
          </Field>
        </div>
      </section>

      <section>
        <SectionHeading>Governing Law & Jurisdiction</SectionHeading>
        <div className="space-y-5">
          <Field label="Governing Law">
            <Input
              placeholder="e.g. Delaware"
              value={data.governingLaw}
              onChange={(e) => set('governingLaw', e.target.value)}
            />
          </Field>
          <Field label="Jurisdiction">
            <Input
              placeholder='e.g. courts located in New Castle, DE'
              value={data.jurisdiction}
              onChange={(e) => set('jurisdiction', e.target.value)}
            />
          </Field>
        </div>
      </section>

      {([1, 2] as const).map((n) => {
        const p = `party${n}` as const
        const fields = [
          [`${p}Name` as const, 'Full Name'],
          [`${p}Title` as const, 'Title'],
          [`${p}Company` as const, 'Company'],
          [`${p}NoticeAddress` as const, 'Notice Address'],
        ] as const
        return (
          <section key={n}>
            <SectionHeading>Party {n}</SectionHeading>
            <div className="space-y-4">
              {fields.map(([key, label]) => (
                <Field key={key} label={label}>
                  <Input
                    value={data[key]}
                    onChange={(e) => set(key, e.target.value)}
                    placeholder={key.endsWith('NoticeAddress') ? 'Email or postal address' : ''}
                  />
                </Field>
              ))}
            </div>
          </section>
        )
      })}

      <div className="pb-8" />
    </div>
  )
}
