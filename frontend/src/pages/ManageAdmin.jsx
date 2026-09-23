import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";

const TABS = ["Homepage & content", "Announcement", "Pages", "Reviews", "Contacts"];

function Field({ label, value, onChange, type = "text", textarea, placeholder }) {
  return (
    <label className="block mb-4">
      <span className="block font-semibold text-brand-green mb-1">{label}</span>
      {textarea ? (
        <textarea value={value || ""} onChange={(e) => onChange(e.target.value)} rows={3} className="w-full rounded-lg border border-[#8C8C8C] px-3 py-2.5" placeholder={placeholder} />
      ) : (
        <input type={type} value={value || ""} onChange={(e) => onChange(e.target.value)} className="w-full rounded-lg border border-[#8C8C8C] px-3 py-2.5" placeholder={placeholder} />
      )}
    </label>
  );
}

function SiteContent() {
  const [c, setC] = useState(null);
  useEffect(() => { api.get("/content/site").then((r) => setC(r.data)); }, []);
  if (!c) return <p>Loading…</p>;
  const set = (k, v) => setC({ ...c, [k]: v });
  const save = async () => {
    try { await api.put("/admin/content/site", { content: c }); toast.success("Homepage content saved"); }
    catch (e) { toast.error(e?.response?.data?.detail || "Save failed"); }
  };
  return (
    <div className="max-w-2xl" data-testid="admin-site-content">
      <p className="text-[#4A4A4D] mb-4">Edit the words and image shown at the top of the homepage. Changes go live immediately.</p>
      <Field label="Eyebrow (small line above the title)" value={c.hero_eyebrow} onChange={(v) => set("hero_eyebrow", v)} />
      <Field label="Main title" value={c.hero_title} onChange={(v) => set("hero_title", v)} />
      <Field label="Highlight line" value={c.hero_highlight} onChange={(v) => set("hero_highlight", v)} />
      <Field label="Body text" value={c.hero_body} onChange={(v) => set("hero_body", v)} textarea />
      <Field label="Hero image URL (optional)" value={c.hero_image} onChange={(v) => set("hero_image", v)} placeholder="https://…" />
      <Field label="Button label" value={c.hero_cta_label} onChange={(v) => set("hero_cta_label", v)} />
      <Field label="Button link" value={c.hero_cta_link} onChange={(v) => set("hero_cta_link", v)} />
      <button onClick={save} className="rounded-full bg-brand-green text-white px-6 py-2.5 font-semibold" data-testid="save-site-content">Save homepage content</button>
    </div>
  );
}

function Announcement() {
  const [a, setA] = useState(null);
  useEffect(() => { api.get("/admin/announcement").then((r) => setA(r.data)); }, []);
  if (!a) return <p>Loading…</p>;
  const set = (k, v) => setA({ ...a, [k]: v });
  const save = async () => {
    try {
      const payload = { ...a, paths: typeof a.paths === "string" ? a.paths.split(",").map((s) => s.trim()).filter(Boolean) : (a.paths || []) };
      await api.put("/admin/announcement", payload);
      toast.success("Announcement saved. Increase the version to re-show it to people who dismissed it.");
    } catch (e) { toast.error("Save failed"); }
  };
  return (
    <div className="max-w-2xl" data-testid="admin-announcement">
      <label className="flex items-center gap-3 mb-4 font-semibold"><input type="checkbox" checked={!!a.enabled} onChange={(e) => set("enabled", e.target.checked)} className="h-5 w-5" data-testid="ann-enabled" /> Show the announcement bar</label>
      <Field label="Message" value={a.text} onChange={(v) => set("text", v)} textarea />
      <Field label="Link (where clicking the bar goes)" value={a.link} onChange={(v) => set("link", v)} />
      <div className="grid sm:grid-cols-2 gap-4">
        <Field label="Start date/time (optional)" value={a.start_at} onChange={(v) => set("start_at", v)} type="datetime-local" />
        <Field label="End date/time (optional)" value={a.end_at} onChange={(v) => set("end_at", v)} type="datetime-local" />
      </div>
      <Field label="Show only on these paths (comma separated, blank = everywhere)" value={Array.isArray(a.paths) ? a.paths.join(", ") : a.paths} onChange={(v) => set("paths", v)} placeholder="/shop, /product" />
      <div className="grid sm:grid-cols-2 gap-4">
        <Field label="Version (bump to re-show after dismissal)" value={a.version} onChange={(v) => set("version", Number(v) || 1)} type="number" />
        <label className="flex items-center gap-3 mt-8 font-semibold"><input type="checkbox" checked={!!a.dismissible} onChange={(e) => set("dismissible", e.target.checked)} className="h-5 w-5" /> Allow people to dismiss it</label>
      </div>
      <button onClick={save} className="rounded-full bg-brand-green text-white px-6 py-2.5 font-semibold" data-testid="save-announcement">Save announcement</button>
    </div>
  );
}

function Pages() {
  const [pages, setPages] = useState([]);
  const [editing, setEditing] = useState(null);
  const load = () => api.get("/admin/cms/pages").then((r) => setPages(r.data));
  useEffect(() => { load(); }, []);

  const startNew = () => setEditing({ slug: "", title: "", status: "published", sections: [{ type: "text", heading: "", body: "" }] });
  const setSection = (i, k, v) => setEditing({ ...editing, sections: editing.sections.map((s, idx) => idx === i ? { ...s, [k]: v } : s) });
  const addSection = () => setEditing({ ...editing, sections: [...(editing.sections || []), { type: "text", heading: "", body: "" }] });
  const removeSection = (i) => setEditing({ ...editing, sections: editing.sections.filter((_, idx) => idx !== i) });

  const save = async () => {
    try {
      if (editing.id) await api.put(`/admin/cms/pages/${editing.id}`, editing);
      else await api.post("/admin/cms/pages", editing);
      toast.success("Page saved"); setEditing(null); load();
    } catch (e) { toast.error(e?.response?.data?.detail || "Save failed"); }
  };
  const del = async (p) => { if (!window.confirm("Delete this page?")) return; await api.delete(`/admin/cms/pages/${p.id}`); load(); };

  if (editing) return (
    <div className="max-w-2xl" data-testid="admin-page-editor">
      <Field label="Page title" value={editing.title} onChange={(v) => setEditing({ ...editing, title: v })} />
      <Field label="URL slug (e.g. our-story → /p/our-story)" value={editing.slug} onChange={(v) => setEditing({ ...editing, slug: v })} />
      <label className="block mb-4"><span className="block font-semibold text-brand-green mb-1">Status</span>
        <select value={editing.status} onChange={(e) => setEditing({ ...editing, status: e.target.value })} className="rounded-lg border border-[#8C8C8C] px-3 py-2.5">
          <option value="published">Published</option><option value="draft">Draft</option>
        </select>
      </label>
      <h3 className="font-heading font-bold text-brand-green mb-2">Content sections</h3>
      {(editing.sections || []).map((s, i) => (
        <div key={i} className="border border-brand-border rounded-xl p-4 mb-3">
          <Field label="Heading" value={s.heading} onChange={(v) => setSection(i, "heading", v)} />
          <Field label="Text" value={s.body} onChange={(v) => setSection(i, "body", v)} textarea />
          <button onClick={() => removeSection(i)} className="text-brand-terracotta font-semibold text-sm">Remove section</button>
        </div>
      ))}
      <button onClick={addSection} className="text-brand-green font-semibold mb-4 block">+ Add section</button>
      <div className="flex gap-3">
        <button onClick={save} className="rounded-full bg-brand-green text-white px-6 py-2.5 font-semibold" data-testid="save-page">Save page</button>
        <button onClick={() => setEditing(null)} className="rounded-full border border-brand-border px-6 py-2.5 font-semibold">Cancel</button>
      </div>
    </div>
  );

  return (
    <div data-testid="admin-pages">
      <button onClick={startNew} className="rounded-full bg-brand-green text-white px-5 py-2 font-semibold mb-4" data-testid="new-page-btn">+ New page</button>
      <div className="space-y-2">
        {pages.map((p) => (
          <div key={p.id} className="flex items-center justify-between bg-white rounded-xl border border-brand-border px-4 py-3">
            <div><span className="font-semibold">{p.title}</span> <span className="text-sm text-[#8C8C8C]">/p/{p.slug} · {p.status}</span></div>
            <div className="flex gap-3">
              <Link to={`/p/${p.slug}`} className="text-brand-green underline text-sm" target="_blank" rel="noreferrer">View</Link>
              <button onClick={() => setEditing(p)} className="text-brand-green font-semibold text-sm">Edit</button>
              <button onClick={() => del(p)} className="text-brand-terracotta font-semibold text-sm">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ReviewsModeration() {
  const [reviews, setReviews] = useState([]);
  const [filter, setFilter] = useState("pending");
  const load = () => api.get(`/admin/reviews${filter ? `?status=${filter}` : ""}`).then((r) => setReviews(r.data));
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [filter]);
  const moderate = async (id, status) => { await api.post(`/admin/reviews/${id}/moderate`, { status }); toast.success(`Review ${status}`); load(); };
  return (
    <div data-testid="admin-reviews">
      <div className="flex gap-2 mb-4">
        {["pending", "approved", "rejected", ""].map((f) => (
          <button key={f} onClick={() => setFilter(f)} className={`rounded-full px-4 py-1.5 font-semibold text-sm ${filter === f ? "bg-brand-green text-white" : "border border-brand-border"}`}>{f || "all"}</button>
        ))}
      </div>
      <div className="space-y-3">
        {reviews.length === 0 && <p className="text-[#4A4A4D]">No reviews here.</p>}
        {reviews.map((r) => (
          <div key={r.id} className="bg-white rounded-xl border border-brand-border p-4">
            <div className="font-semibold">{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)} — {r.title || "(no title)"}</div>
            <p className="text-[#2D2D30] my-1">{r.body}</p>
            <div className="text-sm text-[#8C8C8C]">{r.author_name} · order {r.order_reference} · {r.status}</div>
            <div className="flex gap-3 mt-2">
              <button onClick={() => moderate(r.id, "approved")} className="text-brand-green font-semibold text-sm">Approve</button>
              <button onClick={() => moderate(r.id, "rejected")} className="text-brand-terracotta font-semibold text-sm">Reject</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Contacts() {
  const [contacts, setContacts] = useState([]);
  const [q, setQ] = useState("");
  const load = () => api.get(`/admin/contacts${q ? `?q=${encodeURIComponent(q)}` : ""}`).then((r) => setContacts(r.data));
  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);
  const backend = process.env.REACT_APP_BACKEND_URL;
  return (
    <div data-testid="admin-contacts">
      <div className="flex gap-2 mb-4">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search name or email" className="rounded-lg border border-[#8C8C8C] px-3 py-2" />
        <button onClick={load} className="rounded-full bg-brand-green text-white px-5 py-2 font-semibold">Search</button>
        <a href={`${backend}/api/admin/contacts-export.csv`} className="rounded-full border border-brand-border px-5 py-2 font-semibold">Export CSV</a>
      </div>
      <p className="text-sm text-[#8C8C8C] mb-2">{contacts.length} contacts</p>
      <div className="space-y-2">
        {contacts.slice(0, 200).map((c) => (
          <div key={c.email} className="bg-white rounded-xl border border-brand-border px-4 py-3">
            <span className="font-semibold">{c.name || "(no name)"}</span> <span className="text-[#4A4A4D]">{c.email}</span>
            <div className="text-sm text-[#8C8C8C]">{(c.role_tags || []).join(", ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ManageAdmin() {
  const { user } = useAuth();
  const [tab, setTab] = useState(TABS[0]);
  if (user === null) return <div className="gc-container py-20 text-center">Checking access…</div>;
  if (!user || user.role === "customer") return (
    <div className="gc-container py-20 text-center">
      <h1 className="font-heading text-2xl font-bold text-brand-green mb-3">Staff sign-in required</h1>
      <Link to="/login" className="text-brand-terracotta underline">Sign in</Link>
    </div>
  );
  return (
    <div className="gc-container py-10" data-testid="manage-admin">
      <h1 className="font-heading text-4xl font-extrabold text-brand-green mb-2">Manage content</h1>
      <p className="text-[#4A4A4D] mb-6">Edit the site yourself — no developer needed. Changes are saved to the database and go live straight away.</p>
      <div className="flex flex-wrap gap-2 mb-8 border-b border-brand-border pb-3">
        {TABS.map((t) => (
          <button key={t} onClick={() => setTab(t)} className={`rounded-full px-4 py-2 font-semibold ${tab === t ? "bg-brand-green text-white" : "border border-brand-border text-brand-green"}`} data-testid={`tab-${t}`}>{t}</button>
        ))}
      </div>
      {tab === "Homepage & content" && <SiteContent />}
      {tab === "Announcement" && <Announcement />}
      {tab === "Pages" && <Pages />}
      {tab === "Reviews" && <ReviewsModeration />}
      {tab === "Contacts" && <Contacts />}
    </div>
  );
}
