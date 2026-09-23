import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { Compass, ArrowRight, Loader2 } from "lucide-react";

export default function FinderWizard() {
  const [config, setConfig] = useState(null);
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();

  useEffect(() => {
    api.get("/finder/config").then((r) => setConfig(r.data)).catch(() => {});
  }, []);

  if (!config) return null;
  const steps = config.steps || [];
  const current = steps[step];

  const choose = async (opt) => {
    const next = { ...answers, [current.id]: opt };
    setAnswers(next);
    if (step < steps.length - 1) {
      setStep(step + 1);
      return;
    }
    // resolve
    setBusy(true);
    const payload = {};
    Object.values(next).forEach((o) => {
      if (o.category) payload.category = o.category;
      if (o.min_price != null) payload.min_price = o.min_price;
      if (o.max_price != null) payload.max_price = o.max_price;
    });
    try {
      const r = await api.post("/finder/resolve", payload);
      nav(r.data.shop_url || "/shop");
    } catch {
      nav("/shop");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-brand-border p-6 md:p-8" data-testid="finder-wizard">
      <div className="flex items-center gap-2 text-brand-green font-heading font-bold text-xl mb-1">
        <Compass size={22} /> Find what you need
      </div>
      <p className="text-[#4A4A4D] mb-5">A few quick questions and we'll point you to the right equipment.</p>
      <div className="flex gap-1.5 mb-5">
        {steps.map((s, i) => (
          <div key={s.id} className={`h-1.5 flex-1 rounded-full ${i <= step ? "bg-brand-green" : "bg-brand-border"}`} />
        ))}
      </div>
      {busy ? (
        <div className="flex items-center gap-2 text-brand-green py-6"><Loader2 className="animate-spin" /> Finding the best matches…</div>
      ) : (
        <div>
          <h3 className="font-heading text-2xl font-bold text-brand-green mb-4">{current.title}</h3>
          <div className="grid sm:grid-cols-2 gap-3">
            {current.options.map((opt, i) => (
              <button
                key={i}
                onClick={() => choose(opt)}
                className="flex items-center justify-between rounded-xl border-2 border-brand-border hover:border-brand-green px-5 py-4 text-left font-semibold text-brand-green transition-colors"
                data-testid={`finder-opt-${step}-${i}`}
              >
                {opt.label} <ArrowRight size={18} />
              </button>
            ))}
          </div>
          {step > 0 && (
            <button onClick={() => setStep(step - 1)} className="mt-4 text-[#4A4A4D] underline" data-testid="finder-back">Back</button>
          )}
        </div>
      )}
    </div>
  );
}
