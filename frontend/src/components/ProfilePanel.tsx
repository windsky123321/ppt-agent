import type { UserProfile } from "../types";

type Props = {
  profiles: UserProfile[];
  activeProfileId: string;
  editingProfile: UserProfile | null;
  onSelect: (profileId: string) => void;
  onEditChange: (profile: UserProfile) => void;
  onSave: () => void;
};

export function ProfilePanel({ profiles, activeProfileId, editingProfile, onSelect, onEditChange, onSave }: Props) {
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">配置档</h2>
      <p className="mt-2 text-sm text-slate-600">选择一个持久化配置档，或在当前页面直接修改它。</p>
      <label className="mt-4 block text-sm text-slate-700">
        当前配置档
        <select className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={activeProfileId} onChange={(event) => onSelect(event.target.value)}>
          <option value="">未选择已保存配置</option>
          {profiles.map((profile) => (
            <option key={profile.id} value={profile.id}>
              {profile.name}
            </option>
          ))}
        </select>
      </label>
      {editingProfile ? (
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Field label="名称" value={editingProfile.name} onChange={(value) => onEditChange({ ...editingProfile, name: value })} />
          <Field label="标题字体" value={editingProfile.title_font} onChange={(value) => onEditChange({ ...editingProfile, title_font: value })} />
          <Field label="正文字体" value={editingProfile.body_font} onChange={(value) => onEditChange({ ...editingProfile, body_font: value })} />
          <label className="text-sm text-slate-700">
            听众
            <select className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={editingProfile.audience} onChange={(event) => onEditChange({ ...editingProfile, audience: event.target.value as UserProfile["audience"] })}>
              {["general", "undergraduate", "graduate", "expert", "investor", "lab_meeting", "thesis_defense"].map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-slate-700">
            首选语言
            <select className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={editingProfile.preferred_language} onChange={(event) => onEditChange({ ...editingProfile, preferred_language: event.target.value as UserProfile["preferred_language"] })}>
              {["en", "zh", "bilingual"].map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-slate-700 md:col-span-2">
            自定义要求
            <textarea className="mt-2 min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2" value={editingProfile.custom_instructions} onChange={(event) => onEditChange({ ...editingProfile, custom_instructions: event.target.value })} />
          </label>
          <label className="text-sm text-slate-700 md:col-span-2">
            长需求模板
            <textarea className="mt-2 min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2" value={editingProfile.long_generation_instruction} onChange={(event) => onEditChange({ ...editingProfile, long_generation_instruction: event.target.value })} />
          </label>
        </div>
      ) : null}
      <button className="mt-4 rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-white" onClick={onSave} disabled={!editingProfile}>
        保存配置档
      </button>
    </section>
  );
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="text-sm text-slate-700">
      {label}
      <input className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}
