// app.js — Lógica do SPA InovaComércio MS
let produtos = [];
let resumo = {};
let esgData = {};

// ================================================================
// BOOTSTRAP
// ================================================================
document.addEventListener('DOMContentLoaded', async () => {
    if (Auth.isLoggedIn()) {
        await aposLogin();
    }
});

async function tentarLogin() {
    const email = document.getElementById('loginEmail').value.trim();
    const senha = document.getElementById('loginSenha').value;
    const erro = document.getElementById('loginErro');

    erro.classList.add('hidden');
    try {
        await Auth.login(email, senha);
        await aposLogin();
    } catch (err) {
        erro.textContent = err.message;
        erro.classList.remove('hidden');
    }
}

async function aposLogin() {
    document.getElementById('loginOverlay').classList.add('hidden');

    const u = Auth.usuario;
    document.getElementById('headerUser').textContent =
        `Perfil: ${(u.role || 'operador').toUpperCase()}`;

    try {
        [resumo, produtos, esgData] = await Promise.all([
            API.getDashboard(),
            API.getProdutos(),
            API.getESG(),
        ]);

        renderKPIs();
        renderTabelaProdutos();
        renderESG();
        renderizarGraficosDashboard();
    } catch (err) {
        console.error('Erro ao carregar dados:', err);
        alert('Falha ao carregar dados da API. Verifique se o backend está em execução.');
    }
}

// ================================================================
// NAVEGAÇÃO
// ================================================================
function mudarAba(target) {
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
    document.getElementById(`view-${target}`).classList.remove('hidden');

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('border-emerald-600', 'text-emerald-600');
        btn.classList.add('border-transparent', 'text-slate-500');
        if (btn.dataset.target === target) {
            btn.classList.remove('border-transparent', 'text-slate-500');
            btn.classList.add('border-emerald-600', 'text-emerald-600');
        }
    });

    if (target === 'dashboard') renderizarGraficosDashboard();
    if (target === 'curvaabc') renderizarCurvaABC();
    if (target === 'auditoria') renderTabelaAuditoria();
}

// ================================================================
// KPIs
// ================================================================
function renderKPIs() {
    const fmt = v => v.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
    document.getElementById('kpiFaturamento').textContent = `R$ ${fmt(resumo.faturamento_mes || 0)}`;
    document.getElementById('kpiVariacao').textContent = `${((resumo.variacao_mom || 0) * 100).toFixed(1)}%`;
    document.getElementById('kpiTicket').textContent = `R$ ${fmt(resumo.ticket_medio || 0)}`;
    document.getElementById('kpiMargem').textContent = `${((resumo.margem_media || 0) * 100).toFixed(1)}%`;
    document.getElementById('kpiRupturas').textContent = resumo.rupturas_ativas || 0;
    document.getElementById('kpiCreditoVerde').textContent = `R$ ${fmt(resumo.credito_verde_saldo || 0)}`;
    document.getElementById('kpiCO2').textContent = `${(esgData.ambiental?.co2_evitado_kg || 0)} kg`;
    document.getElementById('kpiResiduos').textContent = `${(esgData.ambiental?.residuos_kg || 0)} kg`;
}

// ================================================================
// PRODUTOS
// ================================================================
function renderTabelaProdutos() {
    const tbody = document.getElementById('tabelaProdutos');
    tbody.innerHTML = '';

    if (!produtos.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-slate-400">Nenhum produto cadastrado</td></tr>`;
        return;
    }

    produtos.forEach(p => {
        tbody.innerHTML += `
            <tr class="hover:bg-slate-50 border-b border-slate-100">
                <td class="p-3 font-mono text-xs text-slate-500">${p.sku || 'SKU-' + p.id}</td>
                <td class="p-3 font-medium text-slate-800">${escapeHtml(p.produto)}</td>
                <td class="p-3 text-slate-600">${escapeHtml(p.categoria || '—')}</td>
                <td class="p-3 text-slate-600">R$ ${(p.custo || 0).toFixed(2)}</td>
                <td class="p-3 text-slate-600">${(p.markup || 0).toFixed(2)}</td>
                <td class="p-3 font-bold text-emerald-600">R$ ${(p.preco_sugerido || 0).toFixed(2)}</td>
                <td class="p-3 text-slate-600">${((p.margem || 0) * 100).toFixed(1)}%</td>
            </tr>
        `;
    });
}

// ================================================================
// ESG
// ================================================================
function renderESG() {
    const amb = esgData.ambiental || {};
    const soc = esgData.social || {};
    const gov = esgData.governanca || esgData['governança'] || {};

    document.getElementById('esgCO2').textContent = `${amb.co2_evitado_kg || 0} kg`;
    document.getElementById('esgResiduos').textContent = `${amb.residuos_kg || 0} kg`;
    document.getElementById('esgColaboradores').textContent = soc.colaboradores || 0;

    const pct = Math.max(0, Math.min(1, gov.conformidade_pct || 0));
    document.getElementById('esgGovernancaBar').style.width = `${pct * 100}%`;
    document.getElementById('esgGovernancaPct').textContent = `${(pct * 100).toFixed(0)}%`;
}

// ================================================================
// AUDITORIA
// ================================================================
async function renderTabelaAuditoria() {
    const tbody = document.getElementById('tabelaAuditoria');
    tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-400">Carregando...</td></tr>`;

    try {
        const eventos = await API.getAuditoria();
        tbody.innerHTML = '';

        if (!eventos.length) {
            tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-400">Sem eventos</td></tr>`;
            return;
        }

        eventos.forEach(e => {
            const data = e.ts ? new Date(e.ts * 1000).toLocaleString('pt-BR') : '—';
            tbody.innerHTML += `
                <tr class="hover:bg-slate-50 border-b border-slate-100">
                    <td class="p-3 font-mono text-xs text-slate-500">${e.id}</td>
                    <td class="p-3 text-slate-600">${data}</td>
                    <td class="p-3 text-slate-800">${escapeHtml(e.usuario)}</td>
                    <td class="p-3 text-slate-700 font-medium">${escapeHtml(e.evento)}</td>
                    <td class="p-3 text-slate-600">${escapeHtml(e.modulo)}</td>
                </tr>
            `;
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-rose-500">Erro: ${err.message}</td></tr>`;
    }
}

// ================================================================
// SCANNER
// ================================================================
async function processarScan() {
    const codigo = document.getElementById('scanCodigo').value.trim();
    const box = document.getElementById('scanResultado');
    box.classList.remove('hidden');
    box.innerHTML = `<p class="text-sm text-slate-500">Processando...</p>`;

    try {
        const data = await API.realizarScan(codigo);
        const fb = data.feedback || {};
        const cor = fb.tipo === 'WARNING' ? 'amber' : 'emerald';

        box.innerHTML = `
            <div class="p-4 bg-${cor}-50 border border-${cor}-200 rounded-lg">
                <p class="font-medium text-${cor}-800">${escapeHtml(fb.mensagem || 'OK')}</p>
            </div>
        `;

        if (data.produtos && data.produtos.length) {
            data.produtos.forEach(p => {
                box.innerHTML += `
                    <div class="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                        <p class="font-semibold text-slate-800">${escapeHtml(p.nome)}</p>
                        <div class="grid grid-cols-3 gap-3 mt-2 text-sm">
                            <div><span class="text-slate-500">Preço:</span> <strong>R$ ${p.preco_venda.toFixed(2)}</strong></div>
                            <div><span class="text-slate-500">Estoque:</span> <strong>${p.estoque_atual}</strong></div>
                            <div><span class="text-slate-500">Mínimo:</span> <strong>${p.estoque_minimo}</strong></div>
                        </div>
                    </div>
                `;
            });
        }
    } catch (err) {
        box.innerHTML = `<p class="text-rose-600 text-sm">Erro: ${escapeHtml(err.message)}</p>`;
    }
}

// ================================================================
// GRÁFICOS
// ================================================================
function renderizarGraficosDashboard() {
    if (typeof Plotly === 'undefined') return;
    if (!produtos.length) return;

    const categorias = {};
    produtos.forEach(p => {
        const cat = p.categoria || 'Outros';
        categorias[cat] = (categorias[cat] || 0) + ((p.estoque_atual || 0) * (p.preco_sugerido || 0));
    });

    Plotly.newPlot('chartCategorias', [{
        values: Object.values(categorias),
        labels: Object.keys(categorias),
        type: 'pie',
        hole: 0.4,
        marker: { colors: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'] },
    }], {
        margin: { t: 20, b: 20, l: 20, r: 20 },
        showlegend: true,
        legend: { orientation: 'h', y: -0.2 },
    }, { responsive: true });
}

async function renderizarCurvaABC() {
    if (typeof Plotly === 'undefined') return;

    try {
        const dados = await API.getCurvaABC();
        const top10 = dados.top10 || [];
        if (!top10.length) return;

        Plotly.newPlot('chartCurvaABC', [{
            x: top10.map(p => p.produto),
            y: top10.map(p => p.faturamento),
            type: 'bar',
            marker: { color: top10.map(p => p.curva === 'A' ? '#10b981' : p.curva === 'B' ? '#f59e0b' : '#ef4444') },
            text: top10.map(p => `Classe ${p.curva}`),
            textposition: 'outside',
        }], {
            margin: { t: 20, b: 100, l: 60, r: 20 },
            xaxis: { tickangle: -30 },
            showlegend: false,
        }, { responsive: true });
    } catch (err) {
        console.error('Erro na Curva ABC:', err);
    }
}

// ================================================================
// PRECIFICAÇÃO
// ================================================================
function calcularPrecificacao() {
    const custo = parseFloat(document.getElementById('simCusto').value) || 0;
    const impostos = parseFloat(document.getElementById('simImpostos').value) || 0;
    const despesas = parseFloat(document.getElementById('simDespesas').value) || 0;
    const margem = parseFloat(document.getElementById('simMargem').value) || 0;

    const pct = (impostos + despesas + margem) / 100;
    if (pct >= 1) {
        alert('A soma dos percentuais não pode ultrapassar 100%.');
        return;
    }

    const divisor = 1 - pct;
    const preco = custo / divisor;

    document.getElementById('resMarkup').textContent = divisor.toFixed(4);
    document.getElementById('resPrecoVenda').textContent = `R$ ${preco.toFixed(2)}`;
    document.getElementById('resultadoSimulador').classList.remove('hidden');
}

// ================================================================
// UTILITÁRIOS
// ================================================================
function escapeHtml(s) {
    return String(s ?? '').replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;',
    }[c]));
}

function alternarTema() {
    document.documentElement.classList.toggle('dark');
    const i = document.getElementById('themeIcon');
    i.classList.toggle('fa-moon');
    i.classList.toggle('fa-sun');
}