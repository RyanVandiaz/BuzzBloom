import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { PieChart, Pie, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { UploadCloud, Filter, Calendar, TrendingUp, BarChart2, PieChart as PieChartIcon, MapPin, Smile, FileText, Download, Zap, BrainCircuit, Lightbulb, AlertTriangle } from 'lucide-react';

// Helper function to parse CSV data - now handles more columns
const parseCSV = (text) => {
    const lines = text.split('\n').filter(line => line.trim() !== '');
    if (lines.length === 0) return [];
    // Make headers case-insensitive and trim spaces
    const headers = lines[0].split(',').map(header => header.trim().toLowerCase());
    const data = [];
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(','); // Don't trim values yet
        if (values.length > headers.length) {
            // Handle commas within a quoted field
            const newValues = [];
            let inQuote = false;
            let currentVal = '';
            for (const val of lines[i].split(',')) {
                if (!inQuote) {
                    if (val.startsWith('"')) {
                        inQuote = true;
                        currentVal += val.substring(1);
                    } else {
                        newValues.push(val);
                    }
                } else {
                    if (val.endsWith('"')) {
                        inQuote = false;
                        currentVal += ',' + val.slice(0, -1);
                        newValues.push(currentVal);
                        currentVal = '';
                    } else {
                        currentVal += ',' + val;
                    }
                }
            }
            if (newValues.length !== headers.length) {
                 console.warn(`Skipping malformed row after attempting to fix commas: ${lines[i]}`);
                 continue;
            }
            values.splice(0, values.length, ...newValues);

        } else if (values.length < headers.length) {
            console.warn(`Skipping malformed row (not enough columns): ${lines[i]}`);
            continue;
        }

        let row = {};
        headers.forEach((header, index) => {
            // Use original header for the key but map from lowercase
            const originalHeader = lines[0].split(',')[index].trim();
            row[originalHeader] = (values[index] || '').trim();
        });
        data.push(row);
    }
    return data;
};

// Colors for charts (Modern & Cool style)
const COLORS = ['#06B6D4', '#6366F1', '#EC4899', '#8B5CF6', '#F59E0B', '#10B981', '#3B82F6', '#EF4444'];

// Function to dynamically load scripts
const loadScript = (src) => {
    return new Promise((resolve, reject) => {
      if (document.querySelector(`script[src="${src}"]`)) {
        resolve();
        return;
      }
      const script = document.createElement('script');
      script.src = src;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Gagal memuat script: ${src}`));
      document.head.appendChild(script);
    });
};

function App() {
    const [originalData, setOriginalData] = useState([]);
    const [cleanedData, setCleanedData] = useState([]);
    const [fileUploaded, setFileUploaded] = useState(false);
    const fileInputRef = useRef(null);
    const dashboardRef = useRef(null);

    // Filter states
    const [platformFilter, setPlatformFilter] = useState('All');
    const [sentimentFilter, setSentimentFilter] = useState('All');
    const [mediaTypeFilter, setMediaTypeFilter] = useState('All');
    const [locationFilter, setLocationFilter] = useState('All');
    const [startDateFilter, setStartDateFilter] = useState('');
    const [endDateFilter, setEndDateFilter] = useState('');

    // Unique values for filters
    const [uniquePlatforms, setUniquePlatforms] = useState([]);
    const [uniqueSentiments, setUniqueSentiments] = useState([]);
    const [uniqueMediaTypes, setUniqueMediaTypes] = useState([]);
    const [uniqueLocations, setUniqueLocations] = useState([]);

    // AI-Generated Insights states
    const [chartInsights, setChartInsights] = useState({ sentiment: '', trend: '', platform: '', mediaType: '', location: '' });
    const [isGeneratingChartInsights, setIsGeneratingChartInsights] = useState({});
    const [campaignSummary, setCampaignSummary] = useState('');
    const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
    const [postIdea, setPostIdea] = useState('');
    const [isGeneratingPost, setIsGeneratingPost] = useState(false);
    const [anomaly, setAnomaly] = useState(null);
    const [anomalyInsight, setAnomalyInsight] = useState('');
    const [isGeneratingAnomalyInsight, setIsGeneratingAnomalyInsight] = useState(false);

    // State for PDF export loading and error
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    
    // Effect for data cleaning and getting unique filter values
    useEffect(() => {
        if (originalData.length > 0) {
            const cleaned = originalData.map(row => {
                const date = new Date(row.Date);
                const engagements = parseInt(row.Engagements) || 0;
                return { ...row, Date: isNaN(date.getTime()) ? null : date, Engagements: engagements };
            }).filter(row => row.Date !== null);
            setCleanedData(cleaned);
            setUniquePlatforms(['All', ...new Set(cleaned.map(d => d.Platform).filter(Boolean))].sort());
            setUniqueSentiments(['All', ...new Set(cleaned.map(d => d.Sentiment).filter(Boolean))].sort());
            setUniqueMediaTypes(['All', ...new Set(cleaned.map(d => d['Media Type']).filter(Boolean))].sort());
            setUniqueLocations(['All', ...new Set(cleaned.map(d => d.Location).filter(Boolean))].sort());
        }
    }, [originalData]);

    const filteredData = useMemo(() => {
        if (cleanedData.length === 0) return [];
        let data = cleanedData;
        if (platformFilter !== 'All') data = data.filter(d => d.Platform === platformFilter);
        if (sentimentFilter !== 'All') data = data.filter(d => d.Sentiment === sentimentFilter);
        if (mediaTypeFilter !== 'All') data = data.filter(d => d['Media Type'] === mediaTypeFilter);
        if (locationFilter !== 'All') data = data.filter(d => d.Location === locationFilter);
        if (startDateFilter) data = data.filter(d => d.Date >= new Date(startDateFilter));
        if (endDateFilter) data = data.filter(d => d.Date <= new Date(endDateFilter));
        return data;
    }, [cleanedData, platformFilter, sentimentFilter, mediaTypeFilter, locationFilter, startDateFilter, endDateFilter]);

    // Reset insights when filter changes
    useEffect(() => {
        setCampaignSummary('');
        setPostIdea('');
        setAnomaly(null);
        setAnomalyInsight('');
        setChartInsights({ sentiment: '', trend: '', platform: '', mediaType: '', location: '' });
    }, [filteredData]);

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const text = e.target.result;
                const parsed = parseCSV(text);
                setOriginalData(parsed);
                setFileUploaded(true);
            };
            reader.readAsText(file);
        }
    };

    // --- Data preparation for charts ---
    const sentimentData = useMemo(() => Object.entries(filteredData.reduce((acc, curr) => {
        acc[curr.Sentiment] = (acc[curr.Sentiment] || 0) + 1;
        return acc;
    }, {})).map(([name, value]) => ({ name, value })), [filteredData]);

    const engagementTrendData = useMemo(() => Object.entries(filteredData.reduce((acc, curr) => {
        if (curr.Date) {
            const dateString = curr.Date.toISOString().split('T')[0];
            acc[dateString] = (acc[dateString] || 0) + curr.Engagements;
        }
        return acc;
    }, {})).map(([date, engagements]) => ({ date, engagements })).sort((a, b) => new Date(a.date) - new Date(b.date)), [filteredData]);

    const platformEngagementData = useMemo(() => Object.entries(filteredData.reduce((acc, curr) => {
        acc[curr.Platform] = (acc[curr.Platform] || 0) + curr.Engagements;
        return acc;
    }, {})).map(([name, value]) => ({ name, value })), [filteredData]);

    const mediaTypeData = useMemo(() => Object.entries(filteredData.reduce((acc, curr) => {
        acc[curr['Media Type']] = (acc[curr['Media Type']] || 0) + 1;
        return acc;
    }, {})).map(([name, value]) => ({ name, value })), [filteredData]);
    
    const locationEngagementData = useMemo(() => Object.entries(filteredData.reduce((acc, curr) => {
        acc[curr.Location] = (acc[curr.Location] || 0) + curr.Engagements;
        return acc;
    }, {})).sort(([, a], [, b]) => b - a).slice(0, 5).map(([name, value]) => ({ name, value })), [filteredData]);

    // Anomaly Detection Logic
    useEffect(() => {
        if (engagementTrendData.length < 7) {
            setAnomaly(null);
            return;
        }
        const engagements = engagementTrendData.map(d => d.engagements);
        const mean = engagements.reduce((a, b) => a + b, 0) / engagements.length;
        const stdDev = Math.sqrt(engagements.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / engagements.length);
        const threshold = 2; // 2 standard deviations from the mean

        let foundAnomaly = null;
        for (const point of engagementTrendData) {
            if (Math.abs(point.engagements - mean) > threshold * stdDev) {
                foundAnomaly = {
                    ...point,
                    type: point.engagements > mean ? 'spike' : 'dip',
                    mean: mean.toFixed(0),
                };
                break; // Find first anomaly and stop
            }
        }
        setAnomaly(foundAnomaly);

    }, [engagementTrendData]);


    // --- Gemini API Call Helper ---
    const getAiInsight = async (prompt) => {
        try {
            const payload = { contents: [{ role: "user", parts: [{ text: prompt }] }] };
            const apiKey = "AIzaSyC0VUu6xTFIwH3aP2R7tbhyu4O8m1ICxn4";
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
            const response = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const result = await response.json();
            if (result.candidates && result.candidates[0]?.content?.parts?.[0]) {
                return result.candidates[0].content.parts[0].text;
            } else {
                return 'Tidak dapat menghasilkan wawasan dari data yang diberikan.';
            }
        } catch (error) {
            console.error('Error fetching AI insight:', error);
            throw error;
        }
    };
    
    const generateSingleChartInsight = async (chartKey) => {
        if (filteredData.length === 0) return;
        
        setIsGeneratingChartInsights(prev => ({ ...prev, [chartKey]: true }));
        setChartInsights(prev => ({ ...prev, [chartKey]: 'Menganalisis...' }));

        const dataMap = {
            sentiment: sentimentData,
            trend: engagementTrendData.slice(-10),
            platform: platformEngagementData,
            mediaType: mediaTypeData,
            location: locationEngagementData,
        };

        const prompts = {
            sentiment: `Anda adalah seorang konsultan intelijen media profesional. Berdasarkan data distribusi sentimen berikut: ${JSON.stringify(dataMap.sentiment)}, berikan 3 wawasan (insights) yang tajam dan dapat ditindaklanjuti untuk strategi komunikasi merek. Fokus pada implikasi strategis dari data ini, bukan hanya deskripsi data. Format sebagai daftar bernomor.`,
            trend: `Anda adalah seorang konsultan intelijen media. Berdasarkan data tren keterlibatan harian berikut: ${JSON.stringify(dataMap.trend)}, berikan 3 wawasan strategis. Analisis puncak, penurunan, dan pola umum. Apa artinya ini bagi ritme kampanye dan alokasi sumber daya? Format sebagai daftar bernomor.`,
            platform: `Anda adalah seorang konsultan intelijen media. Berdasarkan data keterlibatan per platform berikut: ${JSON.stringify(dataMap.platform)}, berikan 3 wawasan yang dapat ditindaklanjuti. Identifikasi platform 'juara' dan 'peluang'. Sarankan bagaimana mengoptimalkan strategi konten untuk setiap segmen platform. Format sebagai daftar bernomor.`,
            mediaType: `Anda adalah seorang konsultan intelijen media. Berdasarkan data bauran jenis media berikut: ${JSON.stringify(dataMap.mediaType)}, berikan 3 wawasan strategis. Analisis preferensi audiens berdasarkan format konten. Sarankan peluang dalam diversifikasi atau spesialisasi format. Format sebagai daftar bernomor.`,
            location: `Anda adalah seorang konsultan intelijen media. Berdasarkan data keterlibatan per lokasi berikut: ${JSON.stringify(dataMap.location)}, berikan 3 wawasan geo-strategis. Identifikasi pasar utama dan pasar yang sedang berkembang. Sarankan bagaimana melokalkan konten atau kampanye untuk hasil yang lebih baik. Format sebagai daftar bernomor.`
        };

        try {
            const result = await getAiInsight(prompts[chartKey]);
            setChartInsights(prev => ({ ...prev, [chartKey]: result }));
        } catch (e) {
            setChartInsights(prev => ({ ...prev, [chartKey]: `Gagal menghasilkan wawasan: ${e.message}` }));
        } finally {
            setIsGeneratingChartInsights(prev => ({ ...prev, [chartKey]: false }));
        }
    };

    const generateAnomalyInsight = async () => {
        if (!anomaly) return;
        setIsGeneratingAnomalyInsight(true);
        setAnomalyInsight('Menganalisis anomali...');

        const anomalyDate = new Date(anomaly.date);
        const anomalyDataPoints = filteredData.filter(d => d.Date.toISOString().split('T')[0] === anomaly.date);
        const topHeadlines = anomalyDataPoints
            .sort((a,b) => b.Engagements - a.Engagements)
            .slice(0,3)
            .map(d => d.Headline)
            .filter(Boolean)
            .join(', ');

        const prompt = `Anda adalah seorang analis data intelijen media. Terdeteksi anomali keterlibatan yang signifikan pada tanggal ${anomalyDate.toLocaleDateString('id-ID')}.
        - Jenis Anomali: ${anomaly.type === 'spike' ? 'Lonjakan Tajam' : 'Penurunan Drastis'}
        - Keterlibatan pada hari itu: ${anomaly.engagements.toLocaleString()}
        - Rata-rata keterlibatan: ${anomaly.mean.toLocaleString()}
        - Topik/Judul utama pada hari itu: ${topHeadlines || 'Tidak ada judul spesifik yang tersedia.'}
        - Platform utama pada hari itu: ${[...new Set(anomalyDataPoints.map(d => d.Platform))].join(', ')}

        Berdasarkan data ini, berikan 3 kemungkinan penyebab anomali ini dan 2 rekomendasi tindakan yang harus diambil (satu untuk memanfaatkan jika lonjakan, satu untuk memperbaiki jika penurunan). Format sebagai daftar bernomor.`;
        
        try {
            const result = await getAiInsight(prompt);
            setAnomalyInsight(result);
        } catch (e) {
            setAnomalyInsight(`Gagal menghasilkan wawasan anomali: ${e.message}`);
        } finally {
            setIsGeneratingAnomalyInsight(false);
        }
    };
    
    const generatePostIdea = async () => {
        if(filteredData.length === 0) return;
        setIsGeneratingPost(true);
        setPostIdea('Menghasilkan ide postingan...');

        const platformPerformance = filteredData.reduce((acc, curr) => {
            acc[curr.Platform] = (acc[curr.Platform] || 0) + curr.Engagements;
            return acc;
        }, {});
        const bestPlatform = Object.keys(platformPerformance).reduce((a,b) => platformPerformance[a] > platformPerformance[b] ? a : b, '');
        
        const topPerformingPosts = filteredData
            .filter(d => d.Platform === bestPlatform && d.Sentiment !== 'Negative')
            .sort((a,b) => b.Engagements - a.Engagements)
            .slice(0, 5);

        const bestMediaType = topPerformingPosts[0]?.['Media Type'] || 'any';
        const topHeadlines = topPerformingPosts.map(p => p.Headline).filter(Boolean).join('; ');

        const prompt = `Anda adalah seorang ahli strategi media sosial yang kreatif dan berbasis data. Tugas Anda adalah membuat ide postingan baru berdasarkan analisis data.
        
        Analisis Kinerja Kami:
        - Platform Berkinerja Terbaik: ${bestPlatform}
        - Jenis Media Paling Menarik di Platform Ini: ${bestMediaType}
        - Judul Berkinerja Tinggi (sebagai inspirasi topik): ${topHeadlines || 'Tidak ada judul spesifik yang tersedia.'}
        
        Berdasarkan data ini, buatlah satu contoh postingan untuk platform **${bestPlatform}**. Postingan harus:
        1. Ditulis dalam Bahasa Indonesia.
        2. Memiliki nada yang menarik dan sesuai untuk ${bestPlatform}.
        3. Memberikan saran konsep visual yang jelas (misalnya, "[Saran Visual: Foto close-up produk...]")
        4. Menyertakan 3-5 tagar yang relevan dan berpotensi tren.

        Format output dengan jelas menggunakan judul: "Platform:", "Konten Postingan:", "Saran Visual:", dan "Tagar:".`;

        try {
            const result = await getAiInsight(prompt);
            setPostIdea(result);
        } catch(e) {
            setPostIdea(`Gagal menghasilkan ide postingan: ${e.message}`);
        } finally {
            setIsGeneratingPost(false);
        }
    };
    
    const generateCampaignSummary = async () => {
        setIsGeneratingSummary(true);
        setCampaignSummary('Membuat ringkasan strategi...');
        const prompt = `Anda adalah seorang konsultan strategi media senior. Analisis data dan wawasan kampanye berikut secara komprehensif. Berikan ringkasan eksekutif (3-4 kalimat) diikuti oleh 3 rekomendasi strategis utama yang paling berdampak. Jangan hanya menjelaskan data, berikan implikasi dan langkah selanjutnya yang konkret.

        Wawasan yang sudah ada (jika tersedia):
        - Wawasan Sentimen: ${chartInsights.sentiment || 'Belum dibuat.'}
        - Wawasan Tren: ${chartInsights.trend || 'Belum dibuat.'}
        - Wawasan Platform: ${chartInsights.platform || 'Belum dibuat.'}

        Data Mentah Kinerja Kampanye (gunakan ini jika wawasan di atas belum dibuat atau untuk memperdalam analisis):
        - Distribusi Sentimen: ${JSON.stringify(sentimentData)}
        - Tren Keterlibatan Harian (10 hari terakhir): ${JSON.stringify(engagementTrendData.slice(-10))}
        - Keterlibatan per Platform: ${JSON.stringify(platformEngagementData)}
        - Bauran Jenis Media: ${JSON.stringify(mediaTypeData)}
        - Keterlibatan berdasarkan 5 Lokasi Teratas: ${JSON.stringify(locationEngagementData)}
        
        Fokus pada gambaran besar: Apa cerita utama yang disampaikan oleh data ini? Di mana peluang terbesar kita dan apa risiko utamanya? Format jawaban Anda dengan jelas.`;
        
        const summary = await getAiInsight(prompt).catch(e => `Gagal membuat ringkasan: ${e.message}`);
        setCampaignSummary(summary);
        setIsGeneratingSummary(false);
    };


    // --- Export to PDF Function ---
    const exportDashboardToPdf = async () => {
        setIsLoading(true);
        setError(null);
        try {
          await Promise.all([
            loadScript('https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'),
            loadScript('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js')
          ]);
          if (!dashboardRef.current) throw new Error("Referensi dasbor tidak ditemukan.");
          const { jsPDF } = window.jspdf;
          if (!jsPDF || !window.html2canvas) throw new Error("Library PDF (jsPDF atau html2canvas) tidak dapat dimuat.");
          const elementsToHide = document.querySelectorAll('.no-print');
          elementsToHide.forEach(el => el.style.display = 'none');
          const canvas = await window.html2canvas(dashboardRef.current, { scale: 2, useCORS: true, backgroundColor: '#0f172a' }); // Match bg
          elementsToHide.forEach(el => el.style.display = '');
          const imgData = canvas.toDataURL('image/png');
          const pdf = new jsPDF('p', 'mm', 'a4');
          const imgWidth = 210;
          const pageHeight = 297;
          const imgHeight = canvas.height * imgWidth / canvas.width;
          let heightLeft = imgHeight;
          let position = 0;
          pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
          heightLeft -= pageHeight;
          while (heightLeft >= 0) {
            position = heightLeft - imgHeight;
            pdf.addPage();
            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
          }
          pdf.save('gemini-dashboard-hybrid.pdf');
        } catch (err) {
          console.error("Error saat mengekspor PDF:", err);
          setError(err.message || "Gagal membuat PDF. Coba lagi.");
          const elementsToHide = document.querySelectorAll('.no-print');
          elementsToHide.forEach(el => el.style.display = '');
        } finally {
          setIsLoading(false);
        }
    };
    
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
          return (
            <div className="p-4 bg-slate-700/80 backdrop-blur-sm border border-slate-600 rounded-lg text-slate-200">
              <p className="label font-bold text-cyan-400">{`Tanggal: ${new Date(label).toLocaleDateString('id-ID')}`}</p>
              <p className="intro">{`${payload[0].name} : ${payload[0].value.toLocaleString()}`}</p>
            </div>
          );
        }
        return null;
    };

    // --- Styling Classes ---
    const filterPanelEffect = "bg-slate-800/40 backdrop-blur-lg border border-slate-700";
    const mainPanelEffect = "bg-slate-800/60 backdrop-blur-xl border border-slate-600";
    const insightBoxClass = "mt-4 bg-slate-900/70 p-4 rounded-lg border border-slate-700 min-h-[120px] text-slate-300 whitespace-pre-wrap text-sm";
    
    const chartList = [
        { key: 'sentiment', title: 'Analisis Sentimen', icon: PieChartIcon, data: sentimentData, type: 'pie' },
        { key: 'trend', title: 'Tren Keterlibatan Seiring Waktu', icon: TrendingUp, data: engagementTrendData, type: 'line' },
        { key: 'platform', title: 'Keterlibatan per Platform', icon: BarChart2, data: platformEngagementData, type: 'bar' },
        { key: 'mediaType', title: 'Kombinasi Jenis Media', icon: FileText, data: mediaTypeData, type: 'pie2' },
        { key: 'location', title: '5 Lokasi Teratas', icon: MapPin, data: locationEngagementData, type: 'bar_vertical' }
    ];

    return (
        <div ref={dashboardRef} className={`min-h-screen bg-slate-900 bg-[radial-gradient(at_top_left,_var(--tw-gradient-stops))] from-slate-900 via-slate-900 to-black text-gray-300 p-4 md:p-8 font-sans flex flex-col items-center`}>
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400..900&display=swap');
                .font-orbitron {
                    font-family: 'Orbitron', sans-serif;
                }
            `}</style>
            
            <header className="w-full max-w-7xl mb-8 text-center">
                <h1 className="text-3xl md:text-5xl font-extrabold font-orbitron">
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-indigo-500">
                        Media Intelligence Dashboard
                    </span>
                </h1>
                 <p className="mt-2 text-slate-400">Didukung oleh AI Gemini</p>
            </header>

            {!fileUploaded && (
                <section className={`${filterPanelEffect} p-8 rounded-2xl shadow-2xl shadow-cyan-500/10 mb-12 w-full max-w-xl text-center transition-all duration-300 ease-in-out`}>
                    <h2 className="text-2xl font-semibold text-cyan-400 mb-6 flex items-center justify-center">
                        <UploadCloud className="mr-3 text-cyan-400" size={28} /> Unggah File CSV Anda
                    </h2>
                    <p className="text-slate-400 mb-6">Pastikan file memiliki kolom 'Date', 'Engagements', 'Sentiment', 'Platform', 'Media Type', 'Location', dan (opsional) 'Headline'.</p>
                    <input type="file" accept=".csv" onChange={handleFileUpload} ref={fileInputRef} className="hidden" />
                    <button onClick={() => fileInputRef.current.click()} className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white font-bold py-3 px-8 rounded-lg shadow-lg shadow-cyan-500/20 transition-all transform hover:scale-105 active:scale-95 duration-200 focus:outline-none focus:ring-4 focus:ring-cyan-300">
                        Pilih File
                    </button>
                    <p className="mt-4 text-sm text-slate-500">{fileInputRef.current?.files[0]?.name || "Tidak ada file yang dipilih"}</p>
                </section>
            )}

            {fileUploaded && (
                <div className="w-full max-w-7xl flex flex-col lg:flex-row gap-8">
                    <aside className={`${filterPanelEffect} w-full lg:w-1/4 p-6 rounded-2xl shadow-lg shadow-cyan-500/10 h-fit no-print`}>
                        <h3 className="text-xl font-semibold text-cyan-300 mb-5 flex items-center"><Filter className="mr-2 text-cyan-400" size={24} /> Filter Data</h3>
                        <div className="space-y-4">
                            {[
                                { id: 'platform', label: 'Platform', icon: BarChart2, value: platformFilter, setter: setPlatformFilter, options: uniquePlatforms },
                                { id: 'sentiment', label: 'Sentiment', icon: Smile, value: sentimentFilter, setter: setSentimentFilter, options: uniqueSentiments },
                                { id: 'mediaType', label: 'Media Type', icon: FileText, value: mediaTypeFilter, setter: setMediaTypeFilter, options: uniqueMediaTypes },
                                { id: 'location', label: 'Location', icon: MapPin, value: locationFilter, setter: setLocationFilter, options: uniqueLocations }
                            ].map(filter => (
                                <div key={filter.id}>
                                    <label htmlFor={filter.id} className="block text-sm font-medium text-slate-300 mb-1 flex items-center"><filter.icon className="inline-block mr-2 text-cyan-400" size={16} /> {filter.label}</label>
                                    <select id={filter.id} value={filter.value} onChange={(e) => filter.setter(e.target.value)} className="block w-full py-2 px-3 border border-slate-600 bg-slate-700 text-slate-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm">
                                        {filter.options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                                    </select>
                                </div>
                            ))}
                             <div>
                                <label htmlFor="startDate" className="block text-sm font-medium text-slate-300 mb-1 flex items-center"><Calendar className="inline-block mr-2 text-cyan-400" size={16} /> Tanggal Mulai</label>
                                <input type="date" id="startDate" value={startDateFilter} onChange={(e) => setStartDateFilter(e.target.value)} className="block w-full py-2 px-3 border border-slate-600 bg-slate-700 text-slate-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm" />
                            </div>
                            <div>
                                <label htmlFor="endDate" className="block text-sm font-medium text-slate-300 mb-1 flex items-center"><Calendar className="inline-block mr-2 text-cyan-400" size={16} /> Tanggal Akhir</label>
                                <input type="date" id="endDate" value={endDateFilter} onChange={(e) => setEndDateFilter(e.target.value)} className="block w-full py-2 px-3 border border-slate-600 bg-slate-700 text-slate-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm" />
                            </div>
                             <button onClick={exportDashboardToPdf} className="w-full bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white font-bold py-2 px-4 rounded-lg shadow-lg shadow-teal-500/20 transition-transform transform hover:scale-105 active:scale-95 duration-200 focus:outline-none focus:ring-4 focus:ring-teal-300 flex items-center justify-center mt-6" disabled={isLoading}>
                                {isLoading ? 'Mengekspor...' : <><Download className="mr-2" size={20} /> Ekspor ke PDF</>}
                            </button>
                            {error && <p className="text-red-400 text-sm mt-2 text-center">{error}</p>}
                        </div>
                    </aside>

                    <main className="w-full lg:w-3/4 space-y-8">
                        <section className={`${mainPanelEffect} p-6 rounded-2xl shadow-lg shadow-cyan-500/10`}>
                            <h3 className="text-xl font-semibold text-cyan-300 mb-4 flex items-center"><BrainCircuit className="mr-3 text-cyan-400" size={24} /> Pusat Wawasan AI</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <h4 className='font-semibold text-lg text-slate-200 mb-2 flex items-center'><Zap className='mr-2 text-yellow-400'/> Ringkasan Strategi Kampanye</h4>
                                    <button onClick={generateCampaignSummary} disabled={isGeneratingSummary} className="bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 text-white font-bold py-2 px-4 rounded-lg shadow-md shadow-indigo-500/20 transition-all transform hover:scale-105 active:scale-95 duration-200 focus:outline-none focus:ring-4 focus:ring-indigo-300 flex items-center justify-center mb-4 disabled:opacity-50 disabled:cursor-not-allowed">
                                        {isGeneratingSummary ? 'Membuat...' : <><Zap className="mr-2" size={20} /> Buat Ringkasan</>}
                                    </button>
                                    <div className={insightBoxClass}>
                                        {isGeneratingSummary ? <div className="animate-pulse">[Membuat ringkasan...]</div> : campaignSummary || "Klik untuk membuat ringkasan strategis dari semua data."}
                                    </div>
                                </div>
                                <div>
                                    <h4 className='font-semibold text-lg text-slate-200 mb-2 flex items-center'><Lightbulb className='mr-2 text-yellow-400'/> Generator Ide Konten AI</h4>
                                    <button onClick={generatePostIdea} disabled={isGeneratingPost} className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white font-bold py-2 px-4 rounded-lg shadow-md shadow-amber-500/20 transition-all transform hover:scale-105 active:scale-95 duration-200 focus:outline-none focus:ring-4 focus:ring-amber-300 flex items-center justify-center mb-4 disabled:opacity-50 disabled:cursor-not-allowed">
                                        {isGeneratingPost ? 'Membuat...' : <><Lightbulb className="mr-2" size={20} /> ✨ Buat Ide Postingan</>}
                                    </button>
                                    <div className={insightBoxClass}>
                                        {isGeneratingPost ? <div className="animate-pulse">[Mencari ide terbaik...]</div> : postIdea || "Klik untuk menghasilkan ide postingan berdasarkan data kinerja terbaik Anda."}
                                    </div>
                                </div>
                            </div>
                        </section>

                        {anomaly && (
                            <section className={`p-6 rounded-2xl shadow-lg border-2 border-amber-500 bg-amber-500/10`}>
                                <h3 className="text-xl font-semibold text-amber-300 mb-4 flex items-center"><AlertTriangle className="mr-3 text-amber-400" size={24} /> Peringatan Anomali Terdeteksi!</h3>
                                <p className='text-slate-300 mb-4'>Kami mendeteksi **{anomaly.type === 'spike' ? 'lonjakan' : 'penurunan'}** keterlibatan yang tidak biasa pada **{new Date(anomaly.date).toLocaleDateString('id-ID')}** dengan **{anomaly.engagements.toLocaleString()}** keterlibatan (rata-rata: {anomaly.mean.toLocaleString()}).</p>
                                <button onClick={generateAnomalyInsight} disabled={isGeneratingAnomalyInsight} className="bg-gradient-to-r from-red-500 to-amber-500 hover:from-red-400 hover:to-amber-400 text-white font-bold py-2 px-4 rounded-lg shadow-md shadow-red-500/20 transition-all transform hover:scale-105 active:scale-95 duration-200 focus:outline-none focus:ring-4 focus:ring-red-300 flex items-center justify-center mb-4 disabled:opacity-50 disabled:cursor-not-allowed">
                                    {isGeneratingAnomalyInsight ? 'Menganalisis...' : <><BrainCircuit className="mr-2" size={20} /> ✨ Jelaskan Anomali Ini</>}
                                </button>
                                {anomalyInsight && (
                                     <div className={insightBoxClass}>
                                        {isGeneratingAnomalyInsight ? <div className="animate-pulse">[Menganalisis penyebab...]</div> : anomalyInsight}
                                    </div>
                                )}
                            </section>
                        )}

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            {chartList.map((chart) => (
                                <section key={chart.key} className={`${mainPanelEffect} p-6 rounded-2xl shadow-lg shadow-cyan-500/10`}>
                                    <h3 className="text-xl font-semibold text-cyan-300 mb-4 flex items-center"><chart.icon className="mr-3 text-cyan-400" size={24} /> {chart.title}</h3>
                                    <div className="h-80">
                                        <ResponsiveContainer width="100%" height="100%">
                                        {chart.data.length === 0 ? <div className='flex items-center justify-center h-full text-slate-400'>Tidak ada data untuk ditampilkan.</div> : 
                                        chart.type === 'pie' || chart.type === 'pie2' ? (
                                            <PieChart><Pie data={chart.data} cx="50%" cy="50%" outerRadius={100} fill="#8884d8" dataKey="value" labelLine={false} label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}>{chart.data.map((entry, i) => <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />)}</Pie><Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.8)', border: '1px solid #475569', borderRadius: '0.5rem' }} /><Legend wrapperStyle={{ color: '#94a3b8' }}/></PieChart>
                                        ) : chart.type === 'line' ? (
                                            <LineChart data={chart.data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}><CartesianGrid strokeDasharray="3 3" stroke="#334155" /><XAxis dataKey="date" tickFormatter={(tick) => new Date(tick).toLocaleDateString('id-ID', {day: '2-digit', month: 'short'})} stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip content={<CustomTooltip />} /><Legend wrapperStyle={{ color: '#94a3b8' }}/><Line type="monotone" dataKey="engagements" stroke="#06B6D4" strokeWidth={2} activeDot={{ r: 8, fill: '#06B6D4' }} dot={{ r: 4, fill: '#06B6D4' }} name="Total Keterlibatan" /></LineChart>
                                        ) : chart.type === 'bar' ? (
                                            <BarChart data={chart.data} margin={{ top: 5, right: 20, left: 10, bottom: 35 }}><CartesianGrid strokeDasharray="3 3" stroke="#334155" /><XAxis dataKey="name" angle={-45} textAnchor="end" interval={0} stroke="#94a3b8" height={60} /><YAxis stroke="#94a3b8" /><Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.8)', border: '1px solid #475569', borderRadius: '0.5rem' }} cursor={{fill: 'rgba(100, 116, 139, 0.1)'}}/><Legend wrapperStyle={{ color: '#94a3b8' }}/><Bar dataKey="value" name="Jumlah Keterlibatan" radius={[4, 4, 0, 0]}>{chart.data.map((entry, i) => <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />)}</Bar></BarChart>
                                        ) : ( // bar_vertical
                                            <BarChart data={chart.data} layout="vertical" margin={{ top: 5, right: 20, left: 80, bottom: 5 }}><CartesianGrid strokeDasharray="3 3" stroke="#334155" /><XAxis type="number" stroke="#94a3b8" /><YAxis type="category" dataKey="name" stroke="#94a3b8" width={100} /><Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.8)', border: '1px solid #475569', borderRadius: '0.5rem' }} cursor={{fill: 'rgba(100, 116, 139, 0.1)'}}/><Legend wrapperStyle={{ color: '#94a3b8' }}/><Bar dataKey="value" name="Jumlah Keterlibatan" radius={[0, 4, 4, 0]}>{chart.data.map((entry, i) => <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />)}</Bar></BarChart>
                                        )}
                                        </ResponsiveContainer>
                                    </div>
                                    <div className="mt-4 flex flex-col items-start">
                                        <button onClick={() => generateSingleChartInsight(chart.key)} disabled={isGeneratingChartInsights[chart.key] || chart.data.length === 0} className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white font-bold py-2 px-4 rounded-lg shadow-lg shadow-purple-500/20 transition-all transform hover:scale-105 active:scale-95 duration-200 focus:outline-none focus:ring-4 focus:ring-purple-300 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed">
                                            {isGeneratingChartInsights[chart.key] ? 'Menganalisis...' : <><BrainCircuit className="mr-2" size={20} /> ✨ Buat Wawasan AI</>}
                                        </button>
                                        {chartInsights[chart.key] && (
                                            <div className={`${insightBoxClass} w-full`}>
                                                <h4 className="font-semibold text-cyan-400 mb-2">Insight oleh Gemini AI:</h4>
                                                {chartInsights[chart.key]}
                                            </div>
                                        )}
                                    </div>
                                </section>
                            ))}
                        </div>
                    </main>
                </div>
            )}
        </div>
    );
}

export default App;
