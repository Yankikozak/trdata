"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowDownRight, ArrowUpRight, BarChart3, Bell, ChevronRight, Gauge, Menu, Search, ShieldCheck, SlidersHorizontal, TrendingUp, WalletCards } from "lucide-react";
import PriceChart from "./components/PriceChart";
const fallbackMovers = [
  { s: "ASELS", n: "Aselsan", p: "68.55", c: "+6.42", positive: true },
  { s: "THYAO", n: "Türk Hava Yolları", p: "312.40", c: "+4.17", positive: true },
  { s: "EREGL", n: "Ereğli Demir Çelik", p: "54.20", c: "-3.18", positive: false },
  { s: "KCHOL", n: "Koç Holding", p: "198.90", c: "-2.46", positive: false },
];
const sectors = [
  { n: "Bankacılık", v: "+2.8%", positive: true, w: 24 }, { n: "Ulaştırma", v: "+3.9%", positive: true, w: 11 },
  { n: "Holding", v: "+1.6%", positive: true, w: 18 }, { n: "Enerji", v: "-2.2%", positive: false, w: 8 },
  { n: "Metal", v: "-1.1%", positive: false, w: 9 },
];
type MarketSummary = { demo: boolean; source?: string; index?: { value?: number; change?: number }; movers?: { symbol: string; name: string; price: number; change: number }[] };

function Stat({ label, value, change }: { label: string; value: string; change?: string }) {
  return <div><div className="mono stat-label">{label}</div><div className="stat-value">{value}</div>{change && <div className="mono stat-change">{change}</div>}</div>;
}

export default function Home() {
  const [summary, setSummary] = useState<MarketSummary | null>(null);
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    fetch(`${apiUrl}/api/v1/market/summary`).then((response) => response.json()).then(setSummary).catch(() => undefined);
  }, []);
  const liveIndex = summary?.index;
  const liveMovers = summary?.movers?.map((mover) => ({
    s: mover.symbol, n: mover.name, p: mover.price.toFixed(2), c: `${mover.change >= 0 ? "+" : ""}${mover.change.toFixed(2)}`, positive: mover.change >= 0,
  })) ?? fallbackMovers;
  const indexValue = liveIndex?.value?.toLocaleString("tr-TR", { minimumFractionDigits: 2 }) ?? "10,342.18";
  const indexChange = `${liveIndex?.change?.toFixed(2) ?? "+1.84"}%`;

  return <main className="shell"><div className="page-wrap">
    <header className="topbar">
      <div className="brand-area"><div className="brand-mark"><TrendingUp size={19} /></div><div><div className="mono brand-name">TR-ANALYTIX</div><div className="mono brand-subtitle">BIST INTELLIGENCE</div></div>
        <nav className="mono nav-links"><Link href="/">Piyasa</Link><Link href="/stocks">Hisseler</Link><Link href="/risk-lab">Portföy Lab</Link><Link href="/macro">Makro</Link></nav>
      </div>
      <div className="toolbar"><button aria-label="Search"><Search size={16} /></button><button aria-label="Notifications"><Bell size={16} /></button><button aria-label="Menu" className="menu-button"><Menu size={18} /></button><span className="mono feed-badge">{summary?.demo === false ? "LIVE / DELAYED" : "DEMO FEED"}</span></div>
    </header>

    <section className="intro"><div><div className="mono eyebrow">PAZARTESİ, 27 EYLÜL 2026</div><h1>Piyasanın<br /><i>nabzı.</i></h1><p>BIST verisini, risk sinyallerini ve makro görünümü tek bir analitik çalışma alanında okuyun.</p></div><div className="mono update">SON GÜNCELLEME<br /><span>API BAĞLANTISI</span></div></section>
    <section className="panel stats-grid"><Stat label="BIST 100" value={indexValue} change={`${indexChange} bugün`} /><Stat label="Veri kaynağı" value={summary?.demo === false ? "Yahoo" : "Demo"} change={summary?.source ?? "API bekleniyor"} /><Stat label="İşlem gören" value="487 / 612" change="%79.6 aktif" /><Stat label="Piyasa genişliği" value="1.42" change="↑ pozitif" /></section>

    <section className="main-grid"><div className="panel chart-panel"><div className="panel-heading"><div><div className="mono muted-label">BIST 100 / XU100</div><div className="big-number">{indexValue} <span className="mono positive">{indexChange}</span></div></div><span className="mono live-note">GERÇEK • GECİKMELİ</span></div><PriceChart symbol="XU100" height={285} compact={false} /></div>
      <div className="panel risk-panel"><div className="panel-heading"><div><div className="mono muted-label">RİSK PUSULASI</div><h2>Piyasa skoru</h2></div><ShieldCheck color="#64e6b3" size={23} /></div><div className="risk-score"><div>72</div><span><strong>Temkinli iyimser</strong><small className="mono">Momentum pozitif<br />Volatilite normal</small></span></div><div className="mono risk-list"><span>20G volatilite <b>%18.4</b></span><span>BIST 100 beta <b>1.00</b></span><span>VaR %95 <b>%2.14</b></span></div></div></section>

    <section className="lower-grid"><div className="panel data-panel"><div className="panel-heading"><h2>Günün hareketlileri</h2><ChevronRight size={17} color="#8ca0aa" /></div><div className="mono movers">{liveMovers.map((mover) => <div className="mover" key={mover.s}><b>{mover.s}</b><span>{mover.n}</span><span>{mover.p}</span><span className={mover.positive ? "positive" : "negative"}>{mover.positive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}{mover.c}%</span></div>)}</div></div><div className="panel data-panel"><div className="panel-heading"><h2>Sektör panoraması</h2><BarChart3 size={18} color="#8ca0aa" /></div><div className="sector-list">{sectors.map((sector) => <div key={sector.n}><div className="mono sector-row"><span>{sector.n}</span><span className={sector.positive ? "positive" : "negative"}>{sector.v}</span></div><div className="bar"><div className={sector.positive ? "positive-bar" : "negative-bar"} style={{ width: `${sector.w * 3}%` }} /></div></div>)}</div></div></section>
    <section className="macro-grid"><div className="panel macro-card"><Gauge size={17} color="#64e6b3" /><div className="mono muted-label">POLİTİKA FAİZİ</div><strong>%46.00</strong></div><div className="panel macro-card"><WalletCards size={17} color="#64e6b3" /><div className="mono muted-label">TÜFE YILLIK</div><strong>%39.20</strong></div><div className="panel macro-card"><TrendingUp size={17} color="#ff796d" /><div className="mono muted-label">USD / TRY</div><strong>Yahoo API</strong></div><div className="panel macro-card"><SlidersHorizontal size={17} color="#64e6b3" /><div className="mono muted-label">BRENT PETROL</div><strong>Yahoo API</strong></div></section>
    <footer className="mono footer"><span>TR-ANALYTIX / MARKET INTELLIGENCE</span><span>{summary?.source ?? "DEMO DATA • API BEKLENİYOR"}</span></footer>
  </div></main>;
}
