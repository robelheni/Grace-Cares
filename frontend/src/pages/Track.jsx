import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, gbp } from "@/lib/api";
import { Package, Check, Truck } from "lucide-react";

function Timeline({ steps }) {
  return (
    <ol className="space-y-3" data-testid="track-timeline">
      {steps.map((s) => (
        <li key={s.key} className="flex items-center gap-3">
          <span className={`inline-flex h-7 w-7 items-center justify-center rounded-full ${s.done ? "bg-brand-green text-white" : "bg-brand-border text-[#8C8C8C]"}`}>
            {s.done ? <Check size={16} /> : <span className="h-2 w-2 rounded-full bg-current" />}
          </span>
          <span className={s.done ? "font-semibold text-brand-green" : "text-[#8C8C8C]"}>{s.label}</span>
        </li>
      ))}
    </ol>
  );
}

function OrderView({ order }) {
  return (
    <div className="bg-white rounded-2xl border border-brand-border p-6" data-testid="track-result">
      <div className="flex items-center gap-2 text-brand-green font-heading font-bold text-xl mb-1"><Package size={22} /> Order {order.reference}</div>
      <p className="text-[#4A4A4D] mb-4 capitalize">Status: <strong>{(order.status || "").replace(/_/g, " ")}</strong> · Payment: {order.payment_status}</p>
      <Timeline steps={order.timeline || []} />
      <div className="mt-5 border-t border-brand-border pt-4">
        <h3 className="font-semibold mb-2">Items</h3>
        <ul className="text-[#2D2D30] space-y-1">
          {(order.items || []).map((it, i) => <li key={i}>{it.quantity}× {it.name}</li>)}
        </ul>
        {order.total != null && <div className="mt-3 font-bold">Total: {gbp(order.total)}</div>}
      </div>
      {order.tracking && order.tracking.carrier && (
        <div className="mt-4 flex items-center gap-2 text-brand-green"><Truck size={18} /> {order.tracking.carrier} {order.tracking.number}</div>
      )}
    </div>
  );
}

export default function Track() {
  const [params] = useSearchParams();
  const ref = params.get("ref");
  const token = params.get("token");
  const [order, setOrder] = useState(null);
  const [form, setForm] = useState({ reference: "", email: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (ref && token) {
      api.get(`/track?ref=${encodeURIComponent(ref)}&token=${encodeURIComponent(token)}`)
        .then((r) => setOrder(r.data))
        .catch(() => setError("This tracking link is invalid or has expired."));
    }
  }, [ref, token]);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      const r = await api.post("/track/request", form);
      setOrder(r.data.order);
      window.history.replaceState(null, "", r.data.tracking_path);
    } catch (err) {
      setError(err?.response?.data?.detail || "We couldn't find that order.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="gc-container py-12 max-w-xl" data-testid="track-page">
      <h1 className="font-heading text-4xl font-extrabold text-brand-green mb-3">Track your order</h1>
      <p className="text-lg text-[#4A4A4D] mb-6">No account needed — just enter your order reference and email.</p>
      {order ? (
        <OrderView order={order} />
      ) : (
        <form onSubmit={submit} className="bg-white rounded-2xl border border-brand-border p-6 space-y-3" data-testid="track-form">
          <input required placeholder="Order reference (e.g. GC-12345678)" value={form.reference} onChange={(e) => setForm({ ...form, reference: e.target.value })} className="w-full rounded-lg border border-[#8C8C8C] px-3 py-2.5" data-testid="track-ref" />
          <input required type="email" placeholder="Email used for the order" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="w-full rounded-lg border border-[#8C8C8C] px-3 py-2.5" data-testid="track-email" />
          {error && <p className="text-brand-terracotta font-semibold" data-testid="track-error">{error}</p>}
          <button disabled={busy} className="w-full rounded-full bg-brand-green text-white px-6 py-3 font-semibold disabled:opacity-60" data-testid="track-submit">{busy ? "Looking…" : "Track order"}</button>
        </form>
      )}
    </div>
  );
}
