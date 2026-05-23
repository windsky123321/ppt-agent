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
      <h2 className="text-xl font-semibold text-ink">Profile</h2>
      <p className="mt-2 text-sm text-slate-600">Select a persistent presentation profile or edit the active one inline.</p>
      <label className="mt-4 block text-sm text-slate-700">
        Active Profile
        <select className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={activeProfileId} onChange={(event) => onSelect(event.target.value)}>
          <option value="">No saved profile</option>
          {profiles.map((profile) => (
            <option key={profile.id} value={profile.id}>
              {profile.name}
            </option>
          ))}
        </select>
      </label>
      {editingProfile ? (
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Field label="Name" value={editingProfile.name} onChange={(value) => onEditChange({ ...editingProfile, name: value })} />
          <Field label="Title Font" value={editingProfile.title_font} onChange={(value) => onEditChange({ ...editingProfile, title_font: value })} />
          <Field label="Body Font" value={editingProfile.body_font} onChange={(value) => onEditChange({ ...editingProfile, body_font: value })} />
          <label className="text-sm text-slate-700">
            Audience
            <select className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={editingProfile.audience} onChange={(event) => onEditChange({ ...editingProfile, audience: event.target.value as UserProfile["audience"] })}>
              {["general", "undergraduate", "graduate", "expert", "investor", "lab_meeting", "thesis_defense"].map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-slate-700">
            Preferred Language
            <select className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={editingProfile.preferred_language} onChange={(event) => onEditChange({ ...editingProfile, preferred_language: event.target.value as UserProfile["preferred_language"] })}>
              {["en", "zh", "bilingual"].map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-slate-700 md:col-span-2">
            Custom Instructions
            <textarea className="mt-2 min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2" value={editingProfile.custom_instructions} onChange={(event) => onEditChange({ ...editingProfile, custom_instructions: event.target.value })} />
          </label>
        </div>
      ) : null}
      <button className="mt-4 rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-white" onClick={onSave} disabled={!editingProfile}>
        Save Profile
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
