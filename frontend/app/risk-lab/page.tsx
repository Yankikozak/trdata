import StockSelector from "../components/StockSelector";
import PriceChart from "../components/PriceChart";

export default function RiskLabPage() {
  return <main className="shell"><div className="detail-wrap"><div className="detail-eyebrow mono">PORTFÖY LAB / SENARYO MOTORU</div><div className="workspace-header"><div><h1>Risk laboratuvarı</h1><p>Analiz evrenini seç, portföy ağırlıklarını düzenle ve senaryonu izle.</p></div><StockSelector compact /></div><div className="workspace-grid"><div className="panel workspace-panel"><div className="mono muted-label">PORTFÖY GİRDİLERİ</div><div className="input-grid"><label>Sembol<input defaultValue="THYAO" /></label><label>Ağırlık<input defaultValue="35" type="number" /></label><label>Güven<select defaultValue="95"><option value="95">%95</option><option value="99">%99</option></select></label></div><div className="method-row"><span className="active">Historical VaR</span><span>Parametrik</span><span>Monte Carlo</span></div></div><div className="panel workspace-panel"><div className="mono muted-label">SEÇİLİ VARLIK PERFORMANSI</div><PriceChart symbol="THYAO" height={230} compact /></div></div></div></main>;
}
