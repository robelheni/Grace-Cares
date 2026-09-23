import React, { useState, useEffect } from "react";
import { Link, NavLink, useNavigate, useLocation } from "react-router-dom";
import { Menu, X, ShoppingBasket, User, Search, Heart, Phone, Megaphone, SlidersHorizontal } from "lucide-react";
import { useCart } from "@/context/CartContext";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";

const NAV = [
  { to: "/shop", label: "Shop Care Equipment" },
  { to: "/bundles", label: "Bundles" },
  { to: "/donate-equipment", label: "Donate Equipment" },
  { to: "/get-help", label: "Get Help & Support" },
  { to: "/nhs", label: "NHS & Care Providers" },
  { to: "/events", label: "Events & Activities" },
  { to: "/impact", label: "Our Impact" },
  { to: "/get-involved", label: "Get Involved" },
  { to: "/about", label: "About" },
  { to: "/news", label: "News" },
  { to: "/contact", label: "Contact" },
];

export function Header() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [suggest, setSuggest] = useState(null);
  const [showSuggest, setShowSuggest] = useState(false);
  const { count } = useCart();
  const { user } = useAuth();
  const nav = useNavigate();
  const [announce, setAnnounce] = useState(null);
  const [annDismissed, setAnnDismissed] = useState(false);
  const location = useLocation();
  useEffect(() => {
    api.get("/announcement").then((r) => {
      const a = r.data || {};
      if (a.active) setAnnounce(a);
      else setAnnounce(null);
    }).catch(() => {});
  }, []);
  useEffect(() => {
    if (announce) {
      const key = `gc_announce_dismissed_v${announce.version}`;
      setAnnDismissed(localStorage.getItem(key) === "1");
    }
  }, [announce, location.pathname]);
  const dismissAnnounce = () => {
    if (!announce) return;
    localStorage.setItem(`gc_announce_dismissed_v${announce.version}`, "1");
    setAnnDismissed(true);
  };
  const annPathOk = !announce || !announce.paths || announce.paths.length === 0 ||
    announce.paths.some((p) => location.pathname === p || location.pathname.startsWith(p));
  const showAnnounce = announce && annPathOk && !annDismissed;
  const isAdmin = user && user.role && user.role !== "customer";

  // Predictive type-ahead (debounced)
  useEffect(() => {
    const term = q.trim();
    if (term.length < 2) { setSuggest(null); return; }
    const t = setTimeout(() => {
      api.get(`/search/suggest?q=${encodeURIComponent(term)}`)
        .then((r) => { setSuggest(r.data); setShowSuggest(true); })
        .catch(() => {});
    }, 200);
    return () => clearTimeout(t);
  }, [q]);

  const goProduct = (id) => { setShowSuggest(false); setQ(""); setOpen(false); nav(`/product/${id}`); };
  const goCategory = (id) => { setShowSuggest(false); setQ(""); setOpen(false); nav(`/shop?category_id=${id}`); };
  const submitSearch = (e) => { e.preventDefault(); setShowSuggest(false); nav(`/shop?q=${encodeURIComponent(q)}`); setOpen(false); };

  const hasSuggestions = suggest && ((suggest.products || []).length > 0 || (suggest.categories || []).length > 0 || suggest.did_you_mean);

  return (
    <header className="bg-white border-b border-brand-border sticky top-0 z-50" data-testid="site-header">
      {showAnnounce && (
        <div className="relative bg-brand-lime text-[#003d20]" data-testid="announcement-bar">
          <Link to={announce.link || "/shop"} className="block text-center text-sm font-bold py-2 px-10 hover:underline">
            <Megaphone size={16} className="inline mr-2" />{announce.text}
          </Link>
          {announce.dismissible && (
            <button onClick={dismissAnnounce} className="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:opacity-70" aria-label="Dismiss announcement" data-testid="announcement-dismiss"><X size={16} /></button>
          )}
        </div>
      )}
      <div className="bg-brand-green text-white text-sm">
        <div className="gc-container flex items-center justify-between py-1.5">
          <a href="tel:01543730189" className="flex items-center gap-2 hover:underline" data-testid="header-phone">
            <Phone size={16} /> 01543 730189
          </a>
          <span className="hidden sm:inline">Mon–Fri, 9am–5pm · Lichfield</span>
        </div>
      </div>
      <div className="gc-container flex items-center justify-between py-4 gap-4">
        <Link to="/" className="flex items-center gap-2 shrink-0" data-testid="logo-link">
          <span className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-brand-green text-white font-heading font-bold text-xl">GC</span>
          <span className="font-heading font-extrabold text-2xl text-brand-green leading-none">Grace&nbsp;Cares</span>
        </Link>

        <form onSubmit={submitSearch} className="hidden md:flex flex-1 max-w-md" data-testid="header-search-form">
          <div className="relative w-full">
            <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-green" />
            <input
              value={q} onChange={(e) => setQ(e.target.value)}
              onFocus={() => q.trim().length >= 2 && setShowSuggest(true)}
              onBlur={() => setTimeout(() => setShowSuggest(false), 150)}
              placeholder="Search care equipment…"
              aria-label="Search care equipment"
              data-testid="header-search-input"
              className="w-full rounded-full border border-[#8C8C8C] bg-white pl-11 pr-4 py-2.5 text-base focus:border-brand-green"
            />
            {showSuggest && hasSuggestions && (
              <div className="absolute left-0 right-0 top-full mt-2 bg-white border border-brand-border rounded-2xl shadow-lg overflow-hidden z-50" data-testid="search-suggestions">
                {suggest.did_you_mean && (
                  <button type="button" onMouseDown={(e) => { e.preventDefault(); setQ(suggest.did_you_mean); }} className="w-full text-left px-4 py-2.5 text-sm text-[#4A4A4D] hover:bg-brand-green/5 border-b border-brand-border">
                    Did you mean <span className="font-bold text-brand-green">{suggest.did_you_mean}</span>?
                  </button>
                )}
                {(suggest.categories || []).map((c) => (
                  <button key={`c-${c.id}`} type="button" onMouseDown={(e) => { e.preventDefault(); goCategory(c.id); }} className="w-full text-left px-4 py-2.5 hover:bg-brand-green/5 flex items-center gap-2" data-testid={`suggest-cat-${c.id}`}>
                    <SlidersHorizontal size={16} className="text-brand-green" /> <span className="font-semibold text-brand-green">{c.name}</span>
                    <span className="text-xs text-[#8C8C8C] ml-auto">Category</span>
                  </button>
                ))}
                {(suggest.products || []).map((p) => (
                  <button key={p.id} type="button" onMouseDown={(e) => { e.preventDefault(); goProduct(p.id); }} className="w-full text-left px-4 py-2.5 hover:bg-brand-green/5 flex items-center gap-3" data-testid={`suggest-product-${p.id}`}>
                    {p.image ? <img src={p.image} alt="" className="h-9 w-9 rounded object-cover" /> : <span className="h-9 w-9 rounded bg-brand-green/10 inline-block" />}
                    <span className="flex-1 min-w-0"><span className="block truncate font-semibold text-[#333]">{p.name}</span></span>
                    {typeof p.price_inc_vat === "number" && <span className="text-brand-green font-bold">£{p.price_inc_vat.toFixed(2)}</span>}
                  </button>
                ))}
                <button type="button" onMouseDown={(e) => { e.preventDefault(); submitSearch(e); }} className="w-full text-center px-4 py-2.5 text-sm font-semibold text-brand-terracotta hover:bg-brand-green/5 border-t border-brand-border" data-testid="suggest-see-all">
                  See all results for “{q}”
                </button>
              </div>
            )}
          </div>
        </form>

        <div className="flex items-center gap-1 sm:gap-3">
          <Link to="/wishlist" className="hidden sm:inline-flex p-2 text-brand-green hover:text-brand-terracotta" aria-label="Wishlist" data-testid="wishlist-link"><Heart size={24} /></Link>
          <Link to={user ? (isAdmin ? "/admin" : "/account") : "/login"} className="inline-flex items-center gap-1.5 p-2 text-brand-green hover:text-brand-terracotta font-semibold" data-testid="account-link">
            <User size={24} /><span className="hidden lg:inline">{user ? "My Account" : "Sign in"}</span>
          </Link>
          <Link to="/cart" className="relative inline-flex items-center gap-1.5 p-2 text-brand-green hover:text-brand-terracotta font-semibold" data-testid="cart-link">
            <ShoppingBasket size={24} />
            {count > 0 && <span className="absolute -top-1 -right-1 bg-brand-terracotta text-white text-xs font-bold rounded-full h-5 min-w-5 px-1 flex items-center justify-center" data-testid="cart-count">{count}</span>}
            <span className="hidden lg:inline">Basket</span>
          </Link>
          <Link to="/donate-funds" className="hidden sm:inline-flex bg-brand-lime text-[#003d20] rounded-full px-5 py-2.5 font-bold hover:brightness-95 transition-all" data-testid="donate-funds-btn">Donate</Link>
          <button onClick={() => setOpen(!open)} className="lg:hidden p-2 text-brand-green" aria-label="Menu" data-testid="mobile-menu-btn">{open ? <X size={28} /> : <Menu size={28} />}</button>
        </div>
      </div>

      <nav className="hidden lg:block border-t border-brand-border bg-white" data-testid="desktop-nav">
        <div className="gc-container flex flex-wrap gap-x-6 gap-y-1 py-2">
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} data-testid={`nav-${n.to.replace('/', '')}`}
              className={({ isActive }) => `py-1 font-semibold text-[15px] hover:text-brand-terracotta hover:underline underline-offset-4 ${isActive ? "text-brand-terracotta underline" : "text-brand-green"}`}>
              {n.label}
            </NavLink>
          ))}
        </div>
      </nav>

      {open && (
        <div className="lg:hidden border-t border-brand-border bg-white" data-testid="mobile-menu">
          <form onSubmit={submitSearch} className="p-4">
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search care equipment…" aria-label="Search" className="w-full rounded-full border border-[#8C8C8C] px-4 py-3" data-testid="mobile-search-input" />
          </form>
          <div className="flex flex-col px-4 pb-4">
            {NAV.map((n) => (
              <Link key={n.to} to={n.to} onClick={() => setOpen(false)} className="py-3 border-b border-brand-border font-semibold text-brand-green text-lg" data-testid={`mnav-${n.to.replace('/', '')}`}>{n.label}</Link>
            ))}
            <Link to="/donate-funds" onClick={() => setOpen(false)} className="mt-4 bg-brand-terracotta text-white rounded-full px-5 py-3 font-semibold text-center">Donate Funds</Link>
          </div>
        </div>
      )}
    </header>
  );
}

export function Footer() {
  return (
    <footer className="bg-brand-green text-white mt-20" data-testid="site-footer">
      <div className="gc-container py-14 grid gap-10 md:grid-cols-4">
        <div>
          <div className="font-heading font-extrabold text-2xl mb-3">Grace Cares</div>
          <p className="text-white/80 text-base">An award-winning not-for-profit CIC in Lichfield, on a mission to make care sustainable.</p>
        </div>
        <div>
          <h4 className="font-heading font-bold text-lg mb-3">Explore</h4>
          <ul className="space-y-2 text-white/80">
            <li><Link to="/shop" className="hover:underline">Shop Equipment</Link></li>
            <li><Link to="/bundles" className="hover:underline">Bundles</Link></li>
            <li><Link to="/track" className="hover:underline">Track my order</Link></li>
            <li><Link to="/donate-equipment" className="hover:underline">Donate Equipment</Link></li>
            <li><Link to="/events" className="hover:underline">Events</Link></li>
            <li><Link to="/resources" className="hover:underline">Care Provider Resources</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-heading font-bold text-lg mb-3">Support</h4>
          <ul className="space-y-2 text-white/80">
            <li><Link to="/get-help" className="hover:underline">Get Help & Support</Link></li>
            <li><Link to="/nhs" className="hover:underline">NHS & Care Providers</Link></li>
            <li><Link to="/get-involved" className="hover:underline">Volunteer</Link></li>
            <li><Link to="/grace-ai" className="hover:underline">Ask Grace (assistant)</Link></li>
            <li><Link to="/faqs" className="hover:underline">FAQs</Link></li>
            <li><Link to="/sustainability" className="hover:underline">Sustainability</Link></li>
            <li><Link to="/privacy" className="hover:underline">Privacy & Cookies</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-heading font-bold text-lg mb-3">Contact</h4>
          <ul className="space-y-2 text-white/80">
            <li><a href="tel:01543730189" className="hover:underline">01543 730189</a></li>
            <li><a href="mailto:hello@grace-cares.com" className="hover:underline">hello@grace-cares.com</a></li>
            <li>Lichfield, Staffordshire</li>
            <li>Mon–Fri, 9am–5pm</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-white/15 py-5 text-center text-white/70 text-sm">
        <div className="flex flex-wrap justify-center gap-x-4 gap-y-2 mb-3">
          <Link to="/faqs" className="hover:underline">FAQs</Link>
          <Link to="/returns" className="hover:underline">Returns & Refunds</Link>
          <Link to="/accessibility" className="hover:underline">Accessibility</Link>
          <Link to="/cookies" className="hover:underline">Cookie Policy</Link>
          <Link to="/terms" className="hover:underline">Terms</Link>
          <Link to="/privacy" className="hover:underline">Privacy</Link>
        </div>
        © {new Date().getFullYear()} Grace Cares CIC · Making care sustainable
      </div>
    </footer>
  );
}

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-brand-bone">
      <Header />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
