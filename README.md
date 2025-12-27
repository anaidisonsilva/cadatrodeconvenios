# 📑 Sistema de Gestão de Convênios

Sistema web desenvolvido em **Django** para **cadastro, controle e acompanhamento de convênios públicos**, com geração de relatórios, filtros avançados, gráficos e exportação em PDF.

O sistema foi pensado para uso em **prefeituras, secretarias e setores administrativos**, facilitando a organização das informações e a tomada de decisão.

---

## ✅ O que o sistema faz

### 📋 Cadastro de Convênios
- Cadastro completo de convênios com:
  - Tipo (Federal, Estadual, Emenda, etc.)
  - Número de convênio, proposta ou indicação
  - Órgão concedente
  - Parlamentar
  - Objeto
  - Valor de repasse
  - Valor de contrapartida
  - Vigência (início e fim)
  - Status do convênio
  - Informação se o **repasse já foi recebido** ou não

### ✏️ Edição e Exclusão
- Editar convênios já cadastrados
- Excluir convênios individualmente
- Excluir **vários convênios em massa** por seleção

### 📊 Dashboard
- Visão geral com:
  - Total de convênios
  - Total de repasses
  - Total de contrapartidas
  - Convênios por tipo
  - Convênios por status
  - Alertas de vigência

### 📈 Relatórios
- Relatórios com filtros avançados:
  - Período (data início e fim)
  - Órgão concedente
  - Parlamentar
  - Tipo
  - Status
  - Repasse recebido (sim / não)
- Gráficos:
  - Convênios por tipo
  - Convênios por status
  - Repasse por mês
- Exportação de relatório em **PDF**, contendo:
  - Filtros aplicados
  - Totais
  - Gráficos
  - Tabela detalhada dos convênios

---

## 🛠️ Tecnologias utilizadas

- Python 3.10+
- Django
- SQLite (pode ser trocado por PostgreSQL ou MySQL)
- Chart.js (gráficos no navegador)
- Matplotlib (gráficos no PDF)
- WeasyPrint (geração de PDF)
- HTML + CSS (Bootstrap)

---

## 💻 Como instalar o projeto (ambiente local)

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/seu-repositorio.git
cd seu-repositorio


## Criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate

## Instalar dependências
pip install -r requirements.txt

## Criar o banco de dado
python manage.py migrate

## Criar usuário administrador (opcional)
python manage.py createsuperuser

## Rodar o servidor

## Rodar o servidor 
python manage.py runserver
http://127.0.0.1:8000

## Estrutura básica do projeto

gestao_convenios/
│
├── convenios/        # App de convênios (cadastro, edição, exclusão)
├── relatorios/       # App de relatórios e PDF
├── core/             # Configurações principais do projeto
├── templates/        # Templates HTML
├── static/           # Arquivos estáticos (CSS, JS)
├── manage.py
└── README.md