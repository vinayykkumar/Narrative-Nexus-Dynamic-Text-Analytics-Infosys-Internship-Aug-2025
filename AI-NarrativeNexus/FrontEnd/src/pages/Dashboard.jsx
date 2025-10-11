import { useEffect, useMemo, useState } from "react"
import { Trash2, RefreshCcw, Download, Sparkles, BarChart2, Tags, Clock } from "lucide-react"
import SentimentDistribution from "../components/charts/SentimentDistribution"
import TopicDistribution from "../components/charts/TopicDistribution"
import KeywordWordCloud from "../components/charts/KeywordWordCloud"
import TopicHighlights from "../components/charts/TopicHighlights"
import TopicConfidenceRadar from "../components/charts/TopicConfidenceRadar"
import { useAuth } from "../contexts/AuthContext"

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000"

const formatDate = (value) => {
	if (!value) return "--"
	try {
		return new Date(value).toLocaleString()
	} catch {
		return String(value)
	}
}

const formatPercentage = (value, digits = 1) => {
	if (typeof value === "number" && Number.isFinite(value)) {
		return `${(value * 100).toFixed(digits)}%`
	}
	const numeric = Number(value)
	if (Number.isFinite(numeric)) {
		return `${(numeric * 100).toFixed(digits)}%`
	}
	return "--"
}

const formatNumber = (value) => {
	if (typeof value === "number" && Number.isFinite(value)) {
		return value.toLocaleString()
	}
	const numeric = Number(value)
	return Number.isFinite(numeric) ? numeric.toLocaleString() : "--"
}

const sentimentTone = {
	positive: { tone: "emerald", emoji: "😊" },
	negative: { tone: "rose", emoji: "😟" },
	neutral: { tone: "slate", emoji: "😐" },
}

const toneClasses = {
	emerald: "bg-emerald-500/10",
	indigo: "bg-indigo-500/10",
	rose: "bg-rose-500/10",
	slate: "bg-slate-500/10",
	amber: "bg-amber-500/10",
}

const MetricCard = ({ icon: Icon, label, value, helper, tone = "indigo" }) => (
	<div className={`relative overflow-hidden rounded-xl border border-white/10 backdrop-blur-sm ${toneClasses[tone] ?? toneClasses.indigo}`}>
		<div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-transparent" aria-hidden="true" />
		<div className="relative p-5 flex items-start gap-4">
			<div className="p-2 rounded-lg bg-black/30 text-white/90">
				<Icon className="w-5 h-5" />
			</div>
			<div className="space-y-1">
				<p className="text-xs tracking-[0.2em] uppercase text-white/60">{label}</p>
				<p className="text-xl font-semibold text-white leading-tight">{value ?? "--"}</p>
				{helper ? <p className="text-xs text-white/70 leading-snug">{helper}</p> : null}
			</div>
		</div>
	</div>
)

const computeTopicKey = (topic, index = 0) => {
	if (!topic) return null
	if (topic.__id) return topic.__id
	if (topic.category_key) return topic.category_key
	if (typeof topic.original_topic_id !== "undefined" && topic.original_topic_id !== null) {
		return `topic-${topic.original_topic_id}`
	}
	if (typeof topic.topic_id !== "undefined" && topic.topic_id !== null) {
		return `topic-${topic.topic_id}`
	}
	return `topic-${index}`
}

const EmptyState = () => (
	<div className="h-full flex flex-col items-center justify-center text-center text-gray-400 gap-2">
		<p className="text-lg font-medium text-white">No saved analyses yet</p>
		<p className="text-sm">
			Run an analysis while logged in, and it will appear here automatically.
		</p>
	</div>
)

const InsightSection = ({ title, children }) => (
	<div className="bg-white/5 border border-white/10 rounded-xl p-5">
		<h3 className="text-lg font-semibold text-white mb-3">{title}</h3>
		{children}
	</div>
)

const Dashboard = () => {
	const { getAuthHeaders, token } = useAuth()
	const [items, setItems] = useState([])
	const [selectedId, setSelectedId] = useState(null)
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState("")
	const [deletingId, setDeletingId] = useState(null)
	const [selectedSentimentKey, setSelectedSentimentKey] = useState(null)
	const [selectedTopicKey, setSelectedTopicKey] = useState(null)
	const [selectedKeyword, setSelectedKeyword] = useState(null)

	const selectedAnalysis = useMemo(
		() => items.find((item) => item.id === selectedId) ?? null,
		[items, selectedId]
	)

	const fetchAnalyses = async () => {
		if (!token) return
		setLoading(true)
		setError("")
		try {
			const response = await fetch(`${API_BASE}/analyses`, {
				headers: { ...getAuthHeaders() },
			})
			if (!response.ok) {
				const data = await response.json().catch(() => ({}))
				throw new Error(data?.detail ?? "Unable to load saved analyses")
			}
			const data = await response.json()
			setItems(Array.isArray(data) ? data : [])
			if (data?.length) {
				setSelectedId((prev) => prev ?? data[0].id)
			} else {
				setSelectedId(null)
			}
		} catch (err) {
			setError(err instanceof Error ? err.message : "Unexpected error")
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => {
		fetchAnalyses()
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [token])

	const handleDelete = async (analysisId) => {
		if (!analysisId) return
		setDeletingId(analysisId)
		try {
			const response = await fetch(`${API_BASE}/analyses/${analysisId}`, {
				method: "DELETE",
				headers: { ...getAuthHeaders() },
			})
			if (!response.ok) {
				const data = await response.json().catch(() => ({}))
				throw new Error(data?.detail ?? "Failed to delete analysis")
			}
			setItems((prev) => prev.filter((item) => item.id !== analysisId))
			if (selectedId === analysisId) {
				setSelectedId((prev) => (prev === analysisId ? null : prev))
			}
		} catch (err) {
			setError(err instanceof Error ? err.message : "Failed to delete analysis")
		} finally {
			setDeletingId(null)
		}
	}

	const handleDownloadJson = async (analysisId) => {
		if (!analysisId) return
		try {
			const response = await fetch(`${API_BASE}/analyses/${analysisId}`, {
				headers: { ...getAuthHeaders() },
			})
			if (!response.ok) {
				throw new Error("Unable to download analysis")
			}
			const data = await response.json()
			const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
			const url = window.URL.createObjectURL(blob)
			const anchor = document.createElement("a")
			anchor.href = url
			anchor.download = `analysis-${analysisId}.json`
			document.body.appendChild(anchor)
			anchor.click()
			document.body.removeChild(anchor)
			window.URL.revokeObjectURL(url)
		} catch (err) {
			setError(err instanceof Error ? err.message : "Unable to download analysis")
		}
	}

	const summary = selectedAnalysis?.insights ?? {}
	const sentimentData = summary?.sentiment ?? null
	const sentimentOverall = sentimentData?.overall ?? (sentimentData?.label ? { label: sentimentData.label, confidence: sentimentData?.confidence, probability: sentimentData?.probability } : null)
	const sentimentLabel = sentimentOverall?.label ? String(sentimentOverall.label).toLowerCase() : null
	const sentimentMeta = sentimentLabel && sentimentTone[sentimentLabel] ? sentimentTone[sentimentLabel] : { tone: "indigo", emoji: "🤔" }
	const sentimentDistribution = sentimentData?.distribution ?? {}
	const hasSentimentData = Boolean(
		sentimentOverall || ["positive", "neutral", "negative"].some((key) => Number(sentimentDistribution?.[key] ?? 0) > 0)
	)

	const rawTopics = Array.isArray(summary?.topics) ? summary.topics : []
	const primaryTopicCandidate = summary?.primary_topic ?? rawTopics[0] ?? null
	const primaryTopicKey = computeTopicKey(primaryTopicCandidate, 0)
	const mergedTopics = (primaryTopicCandidate ? [primaryTopicCandidate, ...rawTopics.filter((topic, index) => computeTopicKey(topic, index + 1) !== primaryTopicKey)] : rawTopics)
	const visualTopics = mergedTopics.map((topic, index) => ({ ...topic, __id: computeTopicKey(topic, index) }))
	const primaryTopic = visualTopics[0] ?? null
	const activeTopic = (selectedTopicKey && visualTopics.find((topic) => topic.__id === selectedTopicKey)) ?? primaryTopic
	const activeTopicKeywords = Array.isArray(activeTopic?.keywords) ? activeTopic.keywords : []
	const activeTopicConfidence = activeTopic?.confidence ?? null
	const activeTopicMentions = activeTopic?.mentions ?? null
	const activeTopicShare = activeTopic?.share ?? activeTopic?.score ?? null
	const topicShare = primaryTopic?.share ?? primaryTopic?.score ?? null

	const keywordWeighted = Array.isArray(summary?.keyword_cloud_weighted) ? summary.keyword_cloud_weighted : []
	const keywordFallback = Array.isArray(summary?.keyword_cloud) ? summary.keyword_cloud : []
	const keywordCloudData = keywordWeighted.length
		? keywordWeighted
			.map((item, index) => {
				const term = item?.term ?? item?.keyword ?? item?.word ?? `keyword-${index}`
				const rawScore = Number(item?.score ?? item?.weight ?? item?.importance ?? 0)
				return {
					term,
					score: Number.isFinite(rawScore) ? rawScore : 0,
				}
			})
			.filter((entry) => entry.term)
		: keywordFallback.map((term, index) => ({ term, score: Math.max(0.05, 1 - index * 0.05) }))
	const keywordCount = keywordCloudData.length
	const keywordTopList = keywordCloudData.slice(0, 8)
	const keywordTopMaxScore = keywordTopList.reduce((acc, item) => (Number.isFinite(item.score) && item.score > acc ? item.score : acc), 0.0001)

	const matchedTerms = Array.isArray(summary?.matched_terms) ? summary.matched_terms : []
	const suggestions = Array.isArray(summary?.suggestions) ? summary.suggestions : []
	const approxWordCount = selectedAnalysis?.metadata?.word_count ?? (selectedAnalysis?.text_preview ? selectedAnalysis.text_preview.split(/\s+/).filter(Boolean).length : null)
	const previewText = selectedAnalysis?.text_preview || "No preview captured for this analysis."
	const suggestionValue = suggestions.length ? `${formatNumber(suggestions.length)} recs` : "No recs saved"
	const suggestionHelper = keywordCount ? `${formatNumber(keywordCount)} keywords surfaced` : "Keywords not stored"
	const keywordLinkedSuggestions = useMemo(() => {
		if (!selectedKeyword) return []
		const lowered = selectedKeyword.toLowerCase()
		return suggestions
			.filter((suggestion) => typeof suggestion === "string" && suggestion.toLowerCase().includes(lowered))
			.slice(0, 3)
	}, [selectedKeyword, suggestions])

	useEffect(() => {
		if (!selectedAnalysis) {
			setSelectedSentimentKey(null)
			setSelectedTopicKey(null)
			setSelectedKeyword(null)
			return
		}
		setSelectedSentimentKey(sentimentLabel ?? null)
		setSelectedTopicKey(primaryTopic ? primaryTopic.__id : null)
		setSelectedKeyword(keywordCloudData?.[0]?.term ?? null)
	}, [selectedAnalysis?.id])

	return (
		<section className="min-h-screen bg-black text-white pt-24 pb-16 px-4 sm:px-8 lg:px-16">
			<div className="max-w-7xl mx-auto">
				<header className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
					<div>
						<h1 className="text-3xl font-semibold">Saved Analyses</h1>
						<p className="text-gray-400 text-sm mt-1">
							Every analysis you run while signed in is stored securely. Revisit insights, export data, or clear entries as needed.
						</p>
					</div>
					<div className="flex gap-3">
						<button
							onClick={fetchAnalyses}
							disabled={loading}
							className="flex items-center gap-2 px-4 py-2 rounded-lg border border-white/20 bg-white/10 text-white text-sm disabled:opacity-50"
						>
							<RefreshCcw className="w-4 h-4" /> Refresh
						</button>
						{selectedAnalysis ? (
							<button
								onClick={() => handleDownloadJson(selectedAnalysis.id)}
								className="flex items-center gap-2 px-4 py-2 rounded-lg border border-indigo-400/30 bg-indigo-500/20 text-indigo-100 text-sm"
							>
								<Download className="w-4 h-4" /> Export JSON
							</button>
						) : null}
					</div>
				</header>

				{error ? (
					<div className="mb-6 p-4 rounded-lg bg-rose-500/20 border border-rose-400/40 text-rose-100 text-sm">
						{error}
					</div>
				) : null}

				<div className="grid lg:grid-cols-12 gap-6 min-h-[60vh]">
					<aside className="lg:col-span-4 bg-white/5 border border-white/10 rounded-xl overflow-hidden">
						<div className="border-b border-white/10 px-5 py-3 flex items-center justify-between text-sm text-gray-300">
							<span>{items.length} saved</span>
						</div>
						{loading ? (
							<div className="p-8 text-center text-gray-400">Loading analyses…</div>
						) : items.length === 0 ? (
							<EmptyState />
						) : (
							<ul className="divide-y divide-white/10">
								{items.map((item) => (
									<li
										key={item.id}
										className={`px-5 py-4 cursor-pointer transition bg-gradient-to-r ${selectedId === item.id ? "from-indigo-500/20 via-transparent" : "from-transparent"}`}
										onClick={() => setSelectedId(item.id)}
									>
										<div className="flex items-start justify-between gap-3">
											<div className="flex-1">
												<p className="text-sm font-medium text-white truncate">
													{item.metadata?.title || item.text_preview?.slice(0, 60) || "Untitled analysis"}
												</p>
												<p className="text-xs text-gray-400 mt-1">{formatDate(item.created_at)}</p>
											</div>
											<button
												className="text-rose-200 hover:text-rose-100"
												onClick={(event) => {
													event.stopPropagation()
													handleDelete(item.id)
												}}
												disabled={deletingId === item.id}
												title="Delete analysis"
											>
												<Trash2 className="w-4 h-4" />
											</button>
										</div>
									</li>
								))}
							</ul>
						)}
					</aside>

					<main className="lg:col-span-8">
						{selectedAnalysis ? (
							<div className="space-y-6">
								<div className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-white/10 via-white/5 to-transparent">
									<div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(99,102,241,0.25),transparent_45%)] opacity-80" aria-hidden="true" />
									<div className="relative p-6 space-y-5">
										<div className="flex flex-wrap items-start justify-between gap-4">
											<div>
												<p className="text-xs uppercase tracking-[0.3em] text-white/60">Analysis title</p>
												<h2 className="text-2xl font-semibold text-white leading-tight">
													{selectedAnalysis.metadata?.title || "Untitled analysis"}
												</h2>
											</div>
											<div className="flex flex-wrap gap-2">
												<span className="px-3 py-1 rounded-full border border-white/20 bg-black/30 text-xs text-gray-100">
													{selectedAnalysis.source ?? "Ad-hoc"}
												</span>
												{selectedAnalysis.include_sentiment === false ? (
													<span className="px-3 py-1 rounded-full border border-amber-400/40 bg-amber-500/20 text-xs text-amber-100">
														Sentiment skipped
													</span>
												) : null}
											</div>
										</div>
										<div className="flex flex-wrap gap-4 text-sm text-indigo-100/80">
											<span className="flex items-center gap-2">
												<Clock className="w-4 h-4" /> Saved {formatDate(selectedAnalysis.created_at)}
											</span>
											{approxWordCount ? (
												<span className="flex items-center gap-2">
													<BarChart2 className="w-4 h-4" /> ≈ {formatNumber(approxWordCount)} words reviewed
												</span>
											) : null}
										</div>
										<div className="bg-black/40 border border-white/10 rounded-xl p-4">
											<p className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">{previewText}</p>
										</div>
									</div>
								</div>

								<div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
									<MetricCard
										icon={Sparkles}
										label="Overall sentiment"
										value={sentimentOverall?.label ? `${sentimentMeta.emoji} ${sentimentOverall.label}` : "Not captured"}
										helper={
											sentimentOverall?.confidence
												? `${formatPercentage(sentimentOverall.confidence)} confidence`
												: selectedAnalysis.include_sentiment === false
												? "Sentiment disabled for this run"
												: "Sentiment data unavailable"
										}
										tone={sentimentMeta.tone}
									/>
									<MetricCard
										icon={BarChart2}
										label="Primary topic"
										value={primaryTopic?.label ?? "No topic stored"}
										helper={
											topicShare
												? `${formatPercentage(topicShare)} coverage`
												: primaryTopic?.keywords?.length
												? primaryTopic.keywords.slice(0, 3).join(", ")
												: "Topic details unavailable"
										}
										tone="amber"
									/>
									<MetricCard
										icon={Tags}
										label="Insights captured"
										value={suggestionValue}
										helper={suggestionHelper}
										tone="emerald"
									/>
								</div>

								<div className="grid lg:grid-cols-2 gap-5">
									<InsightSection title="Summaries">
										<div className="space-y-4 text-sm text-gray-200">
											{summary.extractive_summary ? (
												<div className="p-4 rounded-xl bg-black/30 border border-white/10">
													<p className="text-xs uppercase tracking-[0.25em] text-white/60 mb-2">Extractive</p>
													<p className="leading-relaxed">{summary.extractive_summary}</p>
												</div>
											) : null}
											{summary.abstractive_summary ? (
												<div className="p-4 rounded-xl bg-black/30 border border-white/10">
													<p className="text-xs uppercase tracking-[0.25em] text-white/60 mb-2">Abstractive</p>
													<p className="leading-relaxed">{summary.abstractive_summary}</p>
												</div>
											) : null}
											{!summary.extractive_summary && !summary.abstractive_summary ? (
												<p className="text-gray-400">No summaries captured for this entry.</p>
											) : null}
										</div>
									</InsightSection>
									<InsightSection title={activeTopic ? `Active topic: ${activeTopic.label ?? "Topic"}` : "Topic focus"}>
										{activeTopic ? (
											<div className="space-y-4 text-sm text-gray-200">
												<div className="rounded-xl border border-white/10 bg-black/30 p-4">
													<p className="text-xs uppercase tracking-[0.25em] text-white/60 mb-2">Share</p>
													<p className="text-lg font-semibold text-white">{formatPercentage(activeTopicShare ?? 0)}</p>
													<div className="mt-3 grid grid-cols-2 gap-3 text-xs text-white/70">
														{activeTopicConfidence != null ? (
															<div>
																<p className="uppercase tracking-[0.2em] text-white/40 mb-1">Confidence</p>
																<p className="text-sm text-white">{formatPercentage(activeTopicConfidence)}</p>
															</div>
														) : null}
														{Number.isFinite(activeTopicMentions) ? (
															<div>
																<p className="uppercase tracking-[0.2em] text-white/40 mb-1">Mentions</p>
																<p className="text-sm text-white">{formatNumber(activeTopicMentions)}</p>
															</div>
														) : null}
													</div>
												</div>
												<div className="rounded-xl border border-white/10 bg-black/30 p-4">
													<p className="text-xs uppercase tracking-[0.25em] text-white/60 mb-3">Keywords</p>
													{activeTopicKeywords.length ? (
														<div className="flex flex-wrap gap-2">
															{activeTopicKeywords.map((keyword) => (
																<button
																	type="button"
																	key={keyword}
																	className={`px-3 py-1 rounded-full border text-xs transition ${selectedKeyword === keyword ? "border-indigo-400 bg-indigo-500/20 text-indigo-100" : "border-white/15 bg-white/5 text-white/70 hover:border-white/40"}`}
																	onClick={() => setSelectedKeyword(keyword)}
																>
																	{keyword}
																</button>
															))}
													</div>
													) : (
														<p className="text-xs text-gray-400">No keywords captured for this topic.</p>
													)}
												</div>
											</div>
										) : (
											<p className="text-sm text-gray-400">No topics available for this analysis.</p>
										)}
									</InsightSection>
								</div>

								{hasSentimentData ? (
									<div className="bg-white/5 border border-white/10 rounded-xl p-6">
										<div className="flex flex-wrap items-center justify-between gap-3 mb-4">
											<h3 className="text-lg font-semibold text-white">Sentiment profile</h3>
											{selectedSentimentKey ? (
												<span className="px-3 py-1 rounded-full border border-white/20 bg-white/10 text-xs uppercase tracking-[0.3em] text-white/60">
													Focus: {selectedSentimentKey}
												</span>
											) : null}
										</div>
										<SentimentDistribution
											distribution={sentimentDistribution}
											overallLabel={sentimentOverall?.label ?? null}
											selectedKey={selectedSentimentKey}
											onSegmentSelect={(key) => setSelectedSentimentKey(key ?? null)}
										/>
									</div>
								) : null}

								{visualTopics.length ? (
									<div className="bg-white/5 border border-white/10 rounded-xl p-6 space-y-6">
										<div className="flex flex-wrap items-center justify-between gap-3">
											<h3 className="text-lg font-semibold text-white">Topic intelligence</h3>
											{selectedTopicKey ? (
												<button
													type="button"
													onClick={() => setSelectedTopicKey(primaryTopic ? primaryTopic.__id : null)}
													className="text-xs text-indigo-200 hover:text-indigo-100"
												>
													Reset focus
												</button>
											) : null}
										</div>
										<div className="grid xl:grid-cols-[2fr_1fr] gap-6">
											<div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
												<TopicDistribution
													topics={visualTopics}
													onTopicSelect={(key) => setSelectedTopicKey(key)}
													selectedTopicKey={selectedTopicKey}
												/>
											</div>
											<div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
												<TopicConfidenceRadar topics={visualTopics} />
											</div>
										</div>
										<div className="rounded-2xl border border-white/10 bg-black/20 p-4">
											<TopicHighlights
												topics={visualTopics}
												onTopicSelect={(key) => setSelectedTopicKey(key)}
												selectedTopicKey={selectedTopicKey}
											/>
										</div>
									</div>
								) : null}

								<div className="bg-white/5 border border-white/10 rounded-xl p-6 space-y-6">
									<div className="flex flex-wrap items-center justify-between gap-3">
										<h3 className="text-lg font-semibold text-white">Keyword spotlight</h3>
										{selectedKeyword ? (
											<span className="px-3 py-1 rounded-full border border-white/20 bg-white/10 text-xs uppercase tracking-[0.3em] text-white/60">
												{selectedKeyword}
											</span>
										) : null}
									</div>
									<div className="grid lg:grid-cols-[minmax(0,420px)_1fr] gap-6">
										<div>
											{keywordCloudData.length ? (
												<KeywordWordCloud
													keywords={keywordCloudData}
													onKeywordSelect={(term) => setSelectedKeyword(term)}
													selectedKeyword={selectedKeyword}
												/>
											) : (
												<div className="h-full rounded-3xl border border-white/10 bg-black/30 p-6 text-sm text-gray-400 flex items-center justify-center text-center">
													No keywords were surfaced for this analysis.
												</div>
											)}
										</div>
										<div className="space-y-5">
											<div className="rounded-2xl border border-white/10 bg-black/30 p-5">
												<h4 className="text-sm font-semibold text-white mb-3">Top keywords</h4>
												{keywordTopList.length ? (
													<ul className="space-y-3 text-sm text-gray-200">
														{keywordTopList.map((item, index) => {
															const share = Math.max(0, Math.min(1, item.score / keywordTopMaxScore))
															return (
																<li key={`${item.term}-${index}`} className="space-y-2">
																	<div className="flex items-center justify-between gap-2">
																		<button
																			type="button"
																			className={`text-left font-medium transition ${selectedKeyword === item.term ? "text-indigo-200" : "text-white"}`}
																			onClick={() => setSelectedKeyword(item.term)}
																		>
																			{item.term}
																		</button>
																		<span className="text-xs text-white/60">{formatPercentage(item.score)}</span>
																	</div>
																	<div className="h-1.5 w-full rounded-full bg-white/10 overflow-hidden">
																		<div className="h-full rounded-full bg-indigo-400" style={{ width: `${Math.max(8, share * 100)}%` }} />
																	</div>
																</li>
															)
														})}
													</ul>
												) : (
													<p className="text-sm text-gray-400">No keyword statistics available.</p>
												)}
											</div>
											{matchedTerms.length ? (
												<div className="rounded-2xl border border-white/10 bg-black/30 p-5">
													<h4 className="text-sm font-semibold text-white mb-3">Matched terms</h4>
													<div className="flex flex-wrap gap-2">
														{matchedTerms.map((term, index) => (
															<span
																key={`${term}-${index}`}
																className="px-3 py-1 rounded-full border border-white/10 bg-white/5 text-xs text-gray-200"
															>
																{term}
															</span>
														))}
													</div>
												</div>
											) : null}
										</div>
									</div>
								</div>

								<InsightSection title="Recommendations">
									{suggestions.length ? (
										<div className="space-y-5">
											{selectedKeyword && keywordLinkedSuggestions.length ? (
												<div className="rounded-xl border border-indigo-400/40 bg-indigo-500/10 p-4 text-sm text-indigo-100">
													<p className="font-semibold mb-2">Ideas referencing “{selectedKeyword}”</p>
													<ul className="list-disc pl-5 space-y-1">
														{keywordLinkedSuggestions.map((item, index) => (
															<li key={`kw-suggestion-${index}`}>{item}</li>
														))}
													</ul>
												</div>
											) : null}
											<ul className="grid gap-3 sm:grid-cols-2">
												{suggestions.map((suggestion, index) => (
													<li
														key={index}
														className="relative p-4 rounded-xl bg-black/30 border border-white/10 text-sm leading-relaxed text-gray-200"
													>
														<span className="absolute -left-3 top-4 w-6 h-6 rounded-full bg-indigo-500/30 border border-indigo-400/40 text-[11px] flex items-center justify-center text-indigo-100 font-semibold">
															{index + 1}
														</span>
														<span className="pl-4 block">{suggestion}</span>
													</li>
												))}
											</ul>
										</div>
									) : (
										<p className="text-sm text-gray-400">No actionable recommendations stored.</p>
									)}
								</InsightSection>
							</div>
						) : (
							<EmptyState />
						)}
					</main>
				</div>
			</div>
		</section>
	)
}

export default Dashboard