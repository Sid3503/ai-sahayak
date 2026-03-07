import { useEffect, useMemo, useState } from "react";

const TABS = ["Overview", "Price", "Review", "Insights"];
const DATASET_FALLBACK = ["raju", "ramesh", "suresh", "kanta", "lakshmi"];

/** When embedded from main app with ?retailer=raju, lock to that user only (no dataset switcher). */
function getEmbedRetailer() {
  const p = new URLSearchParams(typeof window !== "undefined" ? window.location.search : "").get("retailer");
  const key = p && typeof p === "string" ? p.toLowerCase().trim() : "";
  return DATASET_FALLBACK.includes(key) ? key : null;
}

function inr(v) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(v || 0));
}

function pct(v) {
  const n = Number(v || 0);
  return `${n >= 0 ? "+" : ""}${n.toFixed(1)}%`;
}

function defaultForecastDate() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function formatTickValue(v) {
  const n = Number(v || 0);
  if (Math.abs(n) >= 100000) return `${(n / 100000).toFixed(1)}L`;
  if (Math.abs(n) >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return `${n.toFixed(0)}`;
}

function cleanExplanationText(text) {
  return String(text || "")
    .replace(/<reasoning>[\s\S]*?<\/reasoning>/gi, "")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/?[^>]+>/g, "")
    .replace(/\*\*/g, "")
    .replace(/^#{1,6}\s*/gm, "")
    .replace(/^-{3,}$/gm, "")
    .replace(/-{4,}/g, " - ")
    .replace(/\|/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function summaryFromExplanation(text) {
  const cleaned = cleanExplanationText(text);
  if (!cleaned) return "";
  const firstBlock = cleaned.split(/\n{2,}/).map((x) => x.trim()).find(Boolean) || cleaned;
  if (firstBlock.length <= 280) return firstBlock;
  const cut = firstBlock.slice(0, 280).replace(/\s+\S*$/, "").trim();
  return `${cut}...`;
}

function candidateName(key) {
  const map = {
    price_base: "Base plan",
    price_optimal: "Recommended plan",
    price_aggressive: "Aggressive plan",
  };
  return map[key] || key;
}

function candidateMeaning(key) {
  const map = {
    price_base: "Steady market posture",
    price_optimal: "Best balance of margin and demand",
    price_aggressive: "Faster share defence",
  };
  return map[key] || "Engine candidate";
}

function LineChart({ values = [], color = "#2563eb", fill = "rgba(37,109,252,0.12)", xLabel = "Time", yLabel = "Value", xTickLabels = [] }) {
  if (!values.length) return <div className="empty">No data yet</div>;
  const width = 320;
  const height = 220;
  const left = 44;
  const right = 20;
  const top = 24;
  const bottom = 38;
  const plotWidth = width - left - right;
  const plotHeight = height - top - bottom;
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const span = Math.max(1, max - min);
  const plotted = values
    .map((v, i) => {
      const x = left + (i / Math.max(1, values.length - 1)) * plotWidth;
      const y = top + plotHeight - ((v - min) / span) * plotHeight;
      return { x, y, value: Number(v || 0), idx: i };
    });
  const points = plotted.map((p) => `${p.x},${p.y}`).join(" ");
  const area = `${left},${top + plotHeight} ${points} ${left + plotWidth},${top + plotHeight}`;
  const tickValues = [max, min + span / 2, min].map((v) => Number(v.toFixed(1)));
  const tickY = [top, top + plotHeight / 2, top + plotHeight];
  const markPoints = plotted.length <= 7 ? plotted : plotted.filter((_, i) => i === 0 || i === plotted.length - 1);
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="line-chart" role="img" aria-label={`${yLabel} over ${xLabel}`}>
      <line x1={left} y1={top + plotHeight} x2={left + plotWidth} y2={top + plotHeight} stroke="rgba(16,32,51,0.14)" strokeWidth="1.2" />
      <line x1={left} y1={top} x2={left} y2={top + plotHeight} stroke="rgba(16,32,51,0.14)" strokeWidth="1.2" />
      {tickY.map((y, idx) => (
        <g key={y}>
          <line x1={left} y1={y} x2={left + plotWidth} y2={y} stroke="rgba(16,32,51,0.06)" strokeWidth="0.9" strokeDasharray="4 5" />
          <text x={left - 8} y={y + 4} className="chart-tick chart-left">{formatTickValue(tickValues[idx])}</text>
        </g>
      ))}
      <polygon points={area} fill={fill} />
      <polyline points={points} fill="none" stroke={color} strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
      {markPoints.map((p) => (
        <g key={`${p.idx}-${p.value}`}>
          <circle cx={p.x} cy={p.y} r="4.5" fill={color} stroke="#fff" strokeWidth="1.6" />
          <text x={p.x} y={Math.max(16, p.y - 10)} className="chart-tick chart-point">{formatTickValue(p.value)}</text>
        </g>
      ))}
      {xTickLabels.length ? plotted.map((p, idx) => (
        <text key={`${p.idx}-label`} x={p.x} y={top + plotHeight + 18} className="chart-tick chart-point chart-xpoint">
          {xTickLabels[idx] || ""}
        </text>
      )) : null}
      <text x={left + plotWidth / 2} y={height - 10} className="chart-axis-label chart-center">{xLabel}</text>
      <text x={left} y={14} className="chart-axis-label chart-top">{yLabel}</text>
    </svg>
  );
}

function BandChart({ base = [], high = [] }) {
  if (!base.length || !high.length) return <div className="empty">Run forecast to view demand band</div>;
  return (
    <div className="band-wrap">
      <LineChart values={high} color="#f59e0b" fill="rgba(245,158,11,0.14)" xLabel="Upcoming days" yLabel="High demand" />
      <LineChart values={base} color="#2563eb" fill="rgba(37,109,252,0.08)" xLabel="Upcoming days" yLabel="Normal demand" />
    </div>
  );
}

function BotCard({ title = "Sahayak Bot", message = "Run the engine to see a plain-language explanation.", source = "deterministic" }) {
  const cleanMessage = cleanExplanationText(message) || "No explanation available yet.";
  return (
    <article className="bot-card">
      <div className="bot-avatar">
        <div className="face">
          <span className="eye eye-left" />
          <span className="eye eye-right" />
          <span className="smile" />
        </div>
      </div>
      <div className="bot-copy">
        <p>{title}</p>
        <div>{cleanMessage}</div>
        <small>{source === "bedrock" ? "Explained by Bedrock LLM" : "Explained by engine summary"}</small>
      </div>
    </article>
  );
}

function ExplanationModal({ open, title, body, onClose, source }) {
  if (!open) return null;
  const blocks = cleanExplanationText(body)
    .split(/\n{2,}/)
    .map((chunk) => chunk.trim())
    .filter(Boolean);
  return (
    <div className="modal-shell" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <h3>{title}</h3>
            <small>{source === "bedrock" ? "Generated by Bedrock LLM" : "Generated by engine summary"}</small>
          </div>
          <button onClick={onClose}>Close</button>
        </div>
        <div className="modal-body">
          {blocks.length ? blocks.map((block, idx) => <p key={`${idx}-${block.slice(0, 20)}`}>{block}</p>) : <p>No detailed explanation available.</p>}
        </div>
      </div>
    </div>
  );
}

function KpiCard({ label, value, sub, tone = "blue" }) {
  return (
    <article className={`kpi-card ${tone}`}>
      <p>{label}</p>
      <h4>{value}</h4>
      <small>{sub}</small>
    </article>
  );
}

function BarList({ items = [], valueKey = "value", labelKey = "label", formatter = (x) => x }) {
  if (!items.length) return <div className="empty">No distribution available</div>;
  const max = Math.max(...items.map((x) => Number(x[valueKey] || 0)), 1);
  return (
    <div className="bar-list">
      {items.map((item) => {
        const width = `${(Number(item[valueKey] || 0) / max) * 100}%`;
        return (
          <div key={String(item[labelKey])} className="bar-row">
            <div className="bar-meta">
              <strong>{item[labelKey]}</strong>
              <span>{formatter(item[valueKey])}</span>
            </div>
            <div className="bar-track">
              <div className="bar-fill" style={{ width }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function MetricChip({ label, value, helper = "" }) {
  return (
    <div className="metric-chip">
      <span>{label}</span>
      <strong>{value}</strong>
      {helper ? <small>{helper}</small> : null}
    </div>
  );
}

export default function App() {
  const embedRetailer = getEmbedRetailer();
  const [tab, setTab] = useState("Overview");
  const [datasetKey, setDatasetKey] = useState(embedRetailer || "raju");
  const [meta, setMeta] = useState({ datasets: [], skus: [], sku_count: 0, rows: 0, active_dataset: embedRetailer || "raju" });
  const [status, setStatus] = useState({});
  const [kpis, setKpis] = useState({ kpis: {}, series: {}, top_skus: [], category_mix: [], payment_mix: [], alerts: [] });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    sku_id: "",
    competitor_price: "",
    inventory_days: "",
    promo_depth_pct: "",
    forecast_days: 14,
    forecast_start: defaultForecastDate(),
  });
  const [whatifText, setWhatifText] = useState("During the Holi rush, competitor drops price to 95, stock cover is only 4 days and promo depth should be 8%");
  const [priceRes, setPriceRes] = useState(null);
  const [whatifRes, setWhatifRes] = useState(null);
  const [forecastRes, setForecastRes] = useState([]);
  const [forecastExplain, setForecastExplain] = useState("");
  const [forecastExplainSource, setForecastExplainSource] = useState("deterministic");
  const [forecastExplainDetail, setForecastExplainDetail] = useState("");
  const [modalState, setModalState] = useState({ open: false, title: "", body: "", source: "deterministic" });
  const [chatDriveToast, setChatDriveToast] = useState("");

  const on = (k, v) => setForm((p) => ({ ...p, [k]: v }));
  const selectedSku = useMemo(() => meta.skus.find((s) => s.sku_id === form.sku_id), [meta.skus, form.sku_id]);
  const currentDatasetLabel = useMemo(() => datasetKey.charAt(0).toUpperCase() + datasetKey.slice(1), [datasetKey]);

  const loadMeta = async (key) => {
    const m = await api(`/api/meta?dataset_key=${encodeURIComponent(key)}`);
    const active = m.active_dataset || key;
    setMeta(m);
    setDatasetKey(embedRetailer || active);
    setForm((prev) => ({ ...prev, sku_id: m.skus?.[0]?.sku_id || prev.sku_id }));
    return { active: embedRetailer || active, firstSku: m.skus?.[0]?.sku_id || "" };
  };

  const loadStatusAndKpis = async (dkey, skuId) => {
    const [st, kp] = await Promise.all([
      api(`/api/model-status?dataset_key=${encodeURIComponent(dkey)}`),
      api(`/api/kpis?dataset_key=${encodeURIComponent(dkey)}${skuId ? `&sku_id=${encodeURIComponent(skuId)}` : ""}`),
    ]);
    setStatus(st);
    setKpis(kp);
  };

  useEffect(() => {
    (async () => {
      try {
        await api("/api/health");
        const initialKey = embedRetailer || "raju";
        const loaded = await loadMeta(initialKey);
        await loadStatusAndKpis(loaded.active, loaded.firstSku);
      } catch (e) {
        setError(`Backend connection failed. Start the backend or point the UI to your EC2 API. Details: ${e.message}`);
      }
    })();
  }, []);

  useEffect(() => {
    if (!datasetKey) return;
    loadStatusAndKpis(datasetKey, form.sku_id).catch((e) => setError(`KPI load failed: ${e.message}`));
  }, [datasetKey, form.sku_id]);

  // When user asks in WP chat, agents call dashboard drive-ui; we poll and auto-navigate, select SKU, show same data (wow factor for judges)
  useEffect(() => {
    const t = setInterval(async () => {
      try {
        const r = await fetch("/api/chat-action");
        if (!r.ok) return;
        const data = await r.json();
        if (!data.action) return;
        const payload = data.payload || {};
        // Optional: switch retailer if chat asked for another dataset (and not embed-locked)
        if (payload.dataset_key && !embedRetailer) {
          if (payload.dataset_key !== datasetKey) loadMeta(payload.dataset_key).catch(() => {});
          setDatasetKey(payload.dataset_key);
        }
        // Optional: select SKU from chat (e.g. user said "sugar" → select Sugar from dropdown)
        if (payload.sku_id) on("sku_id", payload.sku_id);
        if (data.action === "review" || data.action === "price") {
          if (data.payload) setPriceRes(data.payload);
          setTab(data.action === "review" ? "Review" : "Price");
          setChatDriveToast("Live from your chat — same data as WhatsApp reply");
          setTimeout(() => setChatDriveToast(""), 5000);
        } else if (data.action === "insights") {
          setTab("Insights");
          setChatDriveToast("Live from your chat — Insights");
          setTimeout(() => setChatDriveToast(""), 5000);
        } else if (data.action === "overview") {
          setTab("Overview");
          setChatDriveToast("Live from your chat — Overview");
          setTimeout(() => setChatDriveToast(""), 5000);
        }
      } catch (_) {}
    }, 2500);
    return () => clearInterval(t);
  }, [datasetKey]);

  const runPrice = async () => {
    setBusy(true);
    setError("");
    try {
      const out = await api("/api/price", {
        method: "POST",
        body: JSON.stringify({
          dataset_key: datasetKey,
          sku_id: form.sku_id,
          competitor_price: form.competitor_price,
          inventory_days: form.inventory_days,
          promo_depth_pct: form.promo_depth_pct,
        }),
      });
      setPriceRes(out);
      setTab("Price");
    } catch (e) {
      setError(`Price failed: ${e.message}`);
    } finally {
      setBusy(false);
    }
  };

  const runWhatIf = async () => {
    setBusy(true);
    setError("");
    try {
      const out = await api("/api/whatif", {
        method: "POST",
        body: JSON.stringify({
          dataset_key: datasetKey,
          sku_id: form.sku_id,
          scenario: whatifText,
        }),
      });
      setWhatifRes(out);
      setTab("Review");
    } catch (e) {
      setError(`What-if failed: ${e.message}`);
    } finally {
      setBusy(false);
    }
  };

  const runForecast = async () => {
    setBusy(true);
    setError("");
    try {
      const out = await api("/api/forecast", {
        method: "POST",
        body: JSON.stringify({
          dataset_key: datasetKey,
          sku_id: form.sku_id,
          start_date: form.forecast_start,
          days: Number(form.forecast_days || 14),
        }),
      });
      setForecastRes(out.forecast || []);
      setForecastExplain(out.assistant_message || "");
      setForecastExplainSource(out.assistant_source || "deterministic");
      setForecastExplainDetail(out.assistant_detail || "");
      setTab("Insights");
    } catch (e) {
      setError(`Forecast failed: ${e.message}`);
    } finally {
      setBusy(false);
    }
  };

  const k = kpis.kpis || {};
  const series = kpis.series || {};
  const topSkus = kpis.top_skus || [];
  const categoryMix = kpis.category_mix || [];
  const paymentMix = kpis.payment_mix || [];
  const alertList = kpis.alerts || [];

  const priceCandidates = priceRes?.candidates ? Object.entries(priceRes.candidates) : [];
  const candidateLabels = priceCandidates.map(([key]) => candidateName(key));
  const forecastSelection = forecastRes?.[0]?.selection || {};
  const futureRows = forecastRes || [];
  const p50 = futureRows.map((r) => Number(r.demand_quantiles?.p50 || 0));
  const p90 = futureRows.map((r) => Number(r.demand_quantiles?.p90 || 0));
  const priceChart = priceCandidates.map(([, v]) => Number(v.price || 0));
  const unitsChart = priceCandidates.map(([, v]) => Number(v.pred_units || 0));

  const kpiTiles = [
    ["Revenue (30d)", inr(k.revenue_30d), pct(k.revenue_growth_pct), "blue"],
    ["Profit (30d)", inr(k.profit_30d), pct(k.profit_growth_pct), "teal"],
    ["Net Profit (30d)", inr(k.net_profit_30d), "After billing and tax", "sand"],
    ["Units (30d)", Number(k.units_30d || 0).toFixed(0), pct(k.units_growth_pct), "coral"],
    ["Sell Through", `${Number(k.sell_through_pct || 0).toFixed(1)}%`, "Inventory efficiency", "blue"],
    ["Avg Margin", `${Number(k.avg_margin_pct || 0).toFixed(1)}%`, "Gross margin", "teal"],
    ["Price vs Market", `${Number(k.avg_price_gap_pct || 0).toFixed(1)}%`, "Negative means below market", "coral"],
    ["Reorder Risk", Number(k.reorder_risk_skus || 0).toFixed(0), "SKUs below reorder point", "sand"],
    ["Low Cover SKUs", Number(k.low_cover_skus || 0).toFixed(0), "Lead-time exposed", "coral"],
    ["Festival Days", Number(k.festival_days_last30 || 0).toFixed(0), "Demand uplift days", "blue"],
  ];

  const topSkuBars = topSkus.map((row) => ({
    label: `${row.sku_id} ${row.item_name || ""}`.trim(),
    value: Number(row.revenue || 0),
  }));
  const categoryBars = categoryMix.map((row) => ({ label: row.category, value: Number(row.revenue || 0) }));
  const paymentBars = paymentMix.map((row) => ({ label: row.payment_mode, value: Number(row.revenue || 0) }));
  const riskCards = futureRows.slice(0, 6).map((row) => {
    const sel = row.selection || {};
    const p50v = Number(row.demand_quantiles?.p50 || 0);
    const stock = Number(sel.stock_on_hand || 0);
    const reorder = Number(sel.reorder_point || 0);
    const risk = stock <= reorder ? "High" : stock <= p50v ? "Watch" : "Stable";
    return {
      date: row.date,
      risk,
      item_name: sel.item_name || selectedSku?.item_name || "",
      stock,
      reorder,
      price: sel.price_recommended || 0,
    };
  });

  const openExplanation = (title, body, source) => {
    const cleanedBody = cleanExplanationText(body);
    const fallbackBody =
      title === "Full AI Explanation" && tab === "Price"
        ? cleanExplanationText(priceRes?.assistant_detail || priceRes?.assistant_message)
        : title === "Full AI Explanation" && tab === "Review"
          ? cleanExplanationText(whatifRes?.assistant_detail || whatifRes?.assistant_message)
          : cleanExplanationText(forecastExplainDetail || forecastExplain);
    setModalState({
      open: true,
      title,
      body: cleanedBody || fallbackBody || "No detailed explanation available.",
      source: source || "deterministic",
    });
  };

  const isEmbedded = typeof window !== "undefined" && window.self !== window.top;

  return (
    <div className={`page-shell${isEmbedded ? " embed-fit" : ""}`}>
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <div className="page">
        <ExplanationModal
          open={modalState.open}
          title={modalState.title}
          body={modalState.body}
          source={modalState.source}
          onClose={() => setModalState({ open: false, title: "", body: "", source: "deterministic" })}
        />
        {chatDriveToast ? (
          <div className="chat-drive-toast" style={{ padding: "8px 14px", background: "linear-gradient(135deg,#059669,#10b981)", color: "#fff", borderRadius: 8, marginBottom: 8, fontSize: "0.85rem", fontWeight: 600, display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ opacity: 0.9 }}>📱</span>
            {chatDriveToast}
          </div>
        ) : null}
        <nav className="tabs">
          {TABS.map((t) => (
            <button key={t} className={tab === t ? "tab active" : "tab"} onClick={() => setTab(t)}>
              {t}
            </button>
          ))}
        </nav>

        {error ? <div className="error">{error}</div> : null}

        <section className="layout">
          <aside className="left-pane panel">
            <h3>Control Filters</h3>
            <label>Retailer Dataset</label>
            {embedRetailer ? (
              <div className="retailer-locked" style={{ padding: "6px 10px", background: "rgba(16,32,51,0.06)", borderRadius: 6, fontWeight: 600, textTransform: "uppercase" }}>{datasetKey}</div>
            ) : (
              <select value={datasetKey} onChange={(e) => loadMeta(e.target.value).catch((err) => setError(err.message))}>
                {((meta.datasets && meta.datasets.length > 0) ? meta.datasets.map((d) => d.key) : DATASET_FALLBACK).map((k1) => (
                  <option key={k1} value={k1}>{k1.toUpperCase()}</option>
                ))}
              </select>
            )}
            <label>SKU</label>
            <select value={form.sku_id} onChange={(e) => on("sku_id", e.target.value)}>
              {(meta.skus || []).map((x) => <option key={x.sku_id} value={x.sku_id}>{x.sku_id} - {x.item_name}</option>)}
            </select>
            <label>Competitor Price</label>
            <input value={form.competitor_price} onChange={(e) => on("competitor_price", e.target.value)} placeholder="e.g. 199" />
            <label>Inventory Days</label>
            <input value={form.inventory_days} onChange={(e) => on("inventory_days", e.target.value)} placeholder="e.g. 12" />
            <label>Promo Depth %</label>
            <input value={form.promo_depth_pct} onChange={(e) => on("promo_depth_pct", e.target.value)} placeholder="e.g. 8" />
            <label>Forecast Start</label>
            <input type="date" value={form.forecast_start} onChange={(e) => on("forecast_start", e.target.value)} />
            <label>Forecast Days</label>
            <input type="number" min="1" max="30" value={form.forecast_days} onChange={(e) => on("forecast_days", e.target.value)} />
            <div className="side-actions">
              <button onClick={runPrice} disabled={busy}>Run Pricing</button>
              <button onClick={runForecast} disabled={busy}>Run Forecast</button>
            </div>
            <div className="sku-brief">
              <strong>{selectedSku?.item_name || "Select a SKU"}</strong>
              <span>{selectedSku?.category || "Category unavailable"}</span>
            </div>
          </aside>

          <main className="right-pane">
            {tab === "Overview" && (
              <>
                <section className="kpi-grid">
                  {kpiTiles.map(([label, value, sub, tone]) => (
                    <KpiCard key={label} label={label} value={value} sub={sub} tone={tone} />
                  ))}
                </section>

                <section className="hero-strip panel">
                  <div>
                    <p className="eyebrow">Business Pulse</p>
                    <h3>{meta.rows?.toLocaleString?.() || meta.rows} transaction rows across {meta.sku_count || 0} SKUs</h3>
                    <p>Use this board to see revenue momentum, inventory exposure, pricing gap and category contribution in one place.</p>
                  </div>
                  <div className="alert-stack">
                    {(alertList.length ? alertList : ["No major alerts in the current 30-day window."]).slice(0, 3).map((msg) => (
                      <div className="alert-pill" key={msg}>{msg}</div>
                    ))}
                  </div>
                </section>

                <section className="cards-2">
                  <article className="panel">
                    <div className="section-head">
                      <h3>Revenue and Net Profit Trend</h3>
                      <span>Last 30 days</span>
                    </div>
                    <LineChart values={series.revenue || []} color="#2563eb" fill="rgba(37,109,252,0.14)" xLabel="Last 30 days" yLabel="Revenue (INR)" />
                    <LineChart values={series.net_profit || []} color="#0ea5a4" fill="rgba(14,165,164,0.11)" xLabel="Last 30 days" yLabel="Net profit" />
                  </article>
                  <article className="panel">
                    <div className="section-head">
                      <h3>Price Gap and Promo Pressure</h3>
                      <span>Market vs shelf</span>
                    </div>
                    <LineChart values={series.price_gap_pct || []} color="#e86a33" fill="rgba(232,106,51,0.14)" xLabel="Last 30 days" yLabel="Price gap %" />
                    <LineChart values={series.promo_depth_pct || []} color="#8b5cf6" fill="rgba(139,92,246,0.12)" xLabel="Last 30 days" yLabel="Promo %" />
                  </article>
                </section>

                <section className="cards-2">
                  <article className="panel">
                    <div className="section-head">
                      <h3>Top Revenue SKUs</h3>
                      <span>Current dataset</span>
                    </div>
                    <BarList items={topSkuBars} formatter={inr} />
                  </article>
                  <article className="panel">
                    <div className="section-head">
                      <h3>Category Revenue Mix</h3>
                      <span>Where the store earns</span>
                    </div>
                    <BarList items={categoryBars} formatter={inr} />
                  </article>
                </section>
              </>
            )}

            {tab === "Price" && (
              <>
                <section className="cards-2">
                  <article className="panel">
                    <div className="section-head">
                      <h3>Pricing Studio</h3>
                      <button onClick={runPrice} disabled={busy}>Refresh Recommendation</button>
                    </div>
                    <p className="muted">{selectedSku ? `${selectedSku.item_name} (${selectedSku.sku_id})` : "Choose an SKU to evaluate"}</p>
                    <div className="metric-grid">
                      <MetricChip label="Current Price" value={inr(priceRes?.selection?.price_current || 0)} helper="Today's shelf price before any change" />
                      <MetricChip label="Recommended Price" value={inr(priceRes?.selection?.price_recommended || 0)} helper="The engine's preferred selling price" />
                      <MetricChip label="Market Price" value={inr(priceRes?.selection?.market_price || 0)} helper="Observed competitor or market reference price" />
                      <MetricChip label="Expected Margin" value={`${Number(priceRes?.selection?.margin_pct || 0).toFixed(1)}%`} helper="Share of selling price expected as gross margin" />
                      <MetricChip label="Inventory Cover" value={`${Number(priceRes?.selection?.inventory_days_cover || 0).toFixed(1)} d`} helper="How many days current stock may last at recent run-rate" />
                      <MetricChip label="Approval Level" value={priceRes?.selection?.approval || "Pending"} helper="Governance check required before price change" />
                    </div>
                    <div className="final-band">
                      <strong>{priceRes?.selection?.item_name || selectedSku?.item_name || "Selected SKU"}</strong>
                      <span>{priceRes?.selection?.needs_reorder ? "Stock watch active" : "Stock posture healthy"}</span>
                    </div>
                    <BotCard title="Why this price?" message={priceRes?.assistant_message || summaryFromExplanation(priceRes?.assistant_detail) || "Run pricing to hear Sahayak explain the recommendation in simple language."} source={priceRes?.assistant_source || "deterministic"} />
                    <div className="explain-link"><button onClick={() => openExplanation("Full AI Explanation", priceRes?.assistant_detail, priceRes?.assistant_source)}>Open Full Explanation</button></div>
                  </article>
                  <article className="panel">
                    <div className="section-head">
                      <h3>Candidate Price Ladder</h3>
                      <span>Engine comparison</span>
                    </div>
                    <LineChart values={priceChart} color="#2563eb" fill="rgba(37,109,252,0.12)" xLabel="Pricing candidate" yLabel="Recommended selling price (INR)" xTickLabels={candidateLabels} />
                    <div className="chart-note">Base plan = steady posture, Recommended plan = best balance, Aggressive plan = stronger competitive response.</div>
                    <LineChart values={unitsChart} color="#0ea5a4" fill="rgba(14,165,164,0.10)" xLabel="Pricing candidate" yLabel="Expected units sold" xTickLabels={candidateLabels} />
                  </article>
                </section>

                <section className="price-grid">
                  {priceCandidates.map(([key, val]) => (
                    <article key={key} className={`price-box ${priceRes?.selection?.source_key === key ? "active" : ""}`}>
                      <p>{candidateName(key)}</p>
                      <h3>{inr(val.price)}</h3>
                      <small>{candidateMeaning(key)}. {Number(val.pred_units || 0).toFixed(1)} predicted units.</small>
                    </article>
                  ))}
                </section>

                <section className="cards-2">
                  <article className="panel">
                    <div className="section-head">
                      <h3>Commercial Reality</h3>
                    </div>
                    <div className="detail-list">
                      <div><span>Procurement Cost</span><strong>{inr(priceRes?.selection?.purchase_cost || 0)}</strong></div>
                      <div><span>MRP</span><strong>{inr(priceRes?.selection?.mrp || 0)}</strong></div>
                      <div><span>Tax %</span><strong>{Number(priceRes?.selection?.tax_pct || 0).toFixed(1)}%</strong></div>
                      <div><span>Unit Profit</span><strong>{inr(priceRes?.selection?.unit_profit_est || 0)}</strong></div>
                    </div>
                  </article>
                  <article className="panel">
                    <div className="section-head">
                      <h3>Inventory Posture</h3>
                    </div>
                    <div className="detail-list">
                      <div><span>Opening Stock</span><strong>{Number(priceRes?.selection?.opening_stock || 0).toFixed(1)}</strong></div>
                      <div><span>Stock on Hand</span><strong>{Number(priceRes?.selection?.stock_on_hand || 0).toFixed(1)}</strong></div>
                      <div><span>Reorder Point</span><strong>{Number(priceRes?.selection?.reorder_point || 0).toFixed(1)}</strong></div>
                      <div><span>Lead Time</span><strong>{Number(priceRes?.selection?.lead_time_days || 0).toFixed(1)} days</strong></div>
                    </div>
                  </article>
                </section>
              </>
            )}

            {tab === "Review" && (
              <>
                {priceRes?.assistant_message || priceRes?.selection ? (
                  <section className="cards-2" style={{ marginBottom: 16 }}>
                    <article className="panel" style={{ borderLeft: "4px solid #10b981", background: "linear-gradient(135deg, rgba(16,185,129,0.06) 0%, transparent 100%)" }}>
                      <div className="section-head">
                        <h3>Last price run — from your chat</h3>
                        <span style={{ fontSize: "0.75rem", color: "#059669", fontWeight: 600 }}>Same data as WhatsApp reply</span>
                      </div>
                      <p style={{ margin: "0 0 8px", fontSize: "0.95rem", lineHeight: 1.5 }}>{priceRes?.assistant_message || summaryFromExplanation(priceRes?.assistant_detail) || "—"}</p>
                      <div className="detail-list" style={{ marginTop: 8 }}>
                        <div><span>Recommended price</span><strong>{inr(priceRes?.selection?.price_recommended || priceRes?.selection?.price)}</strong></div>
                        <div><span>Item</span><strong>{priceRes?.selection?.item_name || priceRes?.item_name || "—"}</strong></div>
                        <div><span>Margin</span><strong>{Number(priceRes?.selection?.margin_pct || 0).toFixed(1)}%</strong></div>
                      </div>
                    </article>
                  </section>
                ) : null}
                <section className="cards-2">
                  <article className="panel">
                    <div className="section-head">
                      <h3>What-If Scenario</h3>
                      <button onClick={runWhatIf} disabled={busy}>Evaluate</button>
                    </div>
                    <textarea rows={5} value={whatifText} onChange={(e) => setWhatifText(e.target.value)} />
                    <p className="muted">Type natural language. The engine parses competitor moves, stock stress, promo depth and event context.</p>
                    <BotCard title="Sahayak's answer" message={whatifRes?.assistant_message || summaryFromExplanation(whatifRes?.assistant_detail) || "Describe a scenario and click Evaluate to get a simple recommendation summary."} source={whatifRes?.assistant_source || "deterministic"} />
                    <div className="explain-link"><button onClick={() => openExplanation("Full AI Explanation", whatifRes?.assistant_detail, whatifRes?.assistant_source)}>Open Full Explanation</button></div>
                  </article>
                  <article className="panel">
                    <div className="section-head">
                      <h3>Parsed Inputs</h3>
                      <span>How the system understood your request</span>
                    </div>
                    <pre className="json">{JSON.stringify(whatifRes?.overrides || {}, null, 2)}</pre>
                  </article>
                </section>

                <section className="cards-2">
                  <article className="panel">
                    <div className="section-head">
                      <h3>Before vs After</h3>
                    </div>
                    <div className="compare-grid">
                      <div>
                        <span>Original Price</span>
                        <strong>{inr(whatifRes?.original?.selection?.price_recommended || 0)}</strong>
                      </div>
                      <div>
                        <span>Scenario Price</span>
                        <strong>{inr(whatifRes?.updated?.selection?.price_recommended || 0)}</strong>
                      </div>
                      <div>
                        <span>Original Margin</span>
                        <strong>{Number(whatifRes?.original?.selection?.margin_pct || 0).toFixed(1)}%</strong>
                      </div>
                      <div>
                        <span>Scenario Margin</span>
                        <strong>{Number(whatifRes?.updated?.selection?.margin_pct || 0).toFixed(1)}%</strong>
                      </div>
                    </div>
                  </article>
                  <article className="panel">
                    <div className="section-head">
                      <h3>Delta by Candidate</h3>
                    </div>
                    <div className="delta-list">
                      {Object.entries(whatifRes?.delta || {}).map(([key, val]) => (
                        <div key={key}>
                          <span>{key}</span>
                          <strong>{Number(val) >= 0 ? `+${val}` : val}</strong>
                        </div>
                      ))}
                    </div>
                  </article>
                </section>
              </>
            )}

            {tab === "Insights" && (
              <>
                <section className="cards-2">
                  <article className="panel">
                    <div className="section-head">
                      <h3>Demand Band Forecast</h3>
                      <button onClick={runForecast} disabled={busy}>Recompute</button>
                    </div>
                    <BandChart base={p50} high={p90} />
                    <div className="engine-strip">
                      <span>Forecast engine</span>
                      <strong>{forecastRes[0]?.forecast_engine || status.forecast_primary || "N/A"}</strong>
                    </div>
                    <BotCard title="Forecast in simple words" message={forecastExplain || summaryFromExplanation(forecastExplainDetail) || "Run forecast to hear Sahayak explain the expected demand and stock risk."} source={forecastExplainSource} />
                    <div className="explain-link"><button onClick={() => openExplanation("Full AI Explanation", forecastExplainDetail, forecastExplainSource)}>Open Full Explanation</button></div>
                  </article>
                  <article className="panel">
                    <div className="section-head">
                      <h3>Near-Term Decision Snapshot</h3>
                      <span>{forecastSelection.item_name || selectedSku?.item_name || "Selected SKU"}</span>
                    </div>
                    <div className="metric-grid">
                      <MetricChip label="Recommended Price" value={inr(forecastSelection.price_recommended || 0)} />
                      <MetricChip label="Stock on Hand" value={Number(forecastSelection.stock_on_hand || 0).toFixed(1)} />
                      <MetricChip label="Reorder Point" value={Number(forecastSelection.reorder_point || 0).toFixed(1)} />
                      <MetricChip label="Lead Time" value={`${Number(forecastSelection.lead_time_days || 0).toFixed(1)} d`} />
                      <MetricChip label="P50 Demand" value={Number(futureRows[0]?.demand_quantiles?.p50 || 0).toFixed(1)} />
                      <MetricChip label="P90 Demand" value={Number(futureRows[0]?.demand_quantiles?.p90 || 0).toFixed(1)} />
                    </div>
                  </article>
                </section>

                <section className="cards-2">
                  <article className="panel">
                    <div className="section-head">
                      <h3>Next 6 Day Risk Radar</h3>
                      <span>Stock and reorder posture</span>
                    </div>
                    <div className="risk-list">
                      {riskCards.length ? riskCards.map((row) => (
                        <div className={`risk-card risk-${row.risk.toLowerCase()}`} key={row.date}>
                          <div>
                            <strong>{row.date}</strong>
                            <span>{row.item_name || selectedSku?.item_name || form.sku_id}</span>
                          </div>
                          <div>
                            <b>{row.risk}</b>
                            <span>Stock {row.stock.toFixed(1)} / Reorder {row.reorder.toFixed(1)}</span>
                          </div>
                          <div>
                            <b>{inr(row.price)}</b>
                            <span>Recommended price</span>
                          </div>
                        </div>
                      )) : <div className="empty">Run forecast to populate forecast risk radar</div>}
                    </div>
                  </article>
                  <article className="panel">
                    <div className="section-head">
                      <h3>Payment Mode Mix</h3>
                      <span>Commercial convenience</span>
                    </div>
                    <BarList items={paymentBars} formatter={inr} />
                  </article>
                </section>
              </>
            )}
          </main>
        </section>
      </div>
    </div>
  );
}
