# Code Snippets from toollama/soon/notion_api_keys.html

File: `toollama/soon/notion_api_keys.html`  
Language: HTML  
Extracted: 2025-06-07 05:10:28  

## Snippet 1
Lines 3-16

```HTML
/* webkit printing magic: print all background colors */
html {
	-webkit-print-color-adjust: exact;
}
* {
	box-sizing: border-box;
	-webkit-print-color-adjust: exact;
}

html,
body {
	margin: 0;
	padding: 0;
}
```

## Snippet 2
Lines 17-116

```HTML
@media only screen {
	body {
		margin: 2em auto;
		max-width: 900px;
		color: rgb(55, 53, 47);
	}
}

body {
	line-height: 1.5;
	white-space: pre-wrap;
}

a,
a.visited {
	color: inherit;
	text-decoration: underline;
}

.pdf-relative-link-path {
	font-size: 80%;
	color: #444;
}

h1,
h2,
h3 {
	letter-spacing: -0.01em;
	line-height: 1.2;
	font-weight: 600;
	margin-bottom: 0;
}

.page-title {
	font-size: 2.5rem;
	font-weight: 700;
	margin-top: 0;
	margin-bottom: 0.75em;
}

h1 {
	font-size: 1.875rem;
	margin-top: 1.875rem;
}

h2 {
	font-size: 1.5rem;
	margin-top: 1.5rem;
}

h3 {
	font-size: 1.25rem;
	margin-top: 1.25rem;
}

.source {
	border: 1px solid #ddd;
	border-radius: 3px;
	padding: 1.5em;
	word-break: break-all;
}

.callout {
	border-radius: 3px;
	padding: 1rem;
}

figure {
	margin: 1.25em 0;
	page-break-inside: avoid;
}

figcaption {
	opacity: 0.5;
	font-size: 85%;
	margin-top: 0.5em;
}

mark {
	background-color: transparent;
}

.indented {
	padding-left: 1.5em;
}

hr {
	background: transparent;
	display: block;
	width: 100%;
	height: 1px;
	visibility: visible;
	border: none;
	border-bottom: 1px solid rgba(55, 53, 47, 0.09);
}

img {
	max-width: 100%;
}
```

## Snippet 3
Lines 117-123

```HTML
@media only print {
	img {
		max-height: 100vh;
		object-fit: contain;
	}
}
```

## Snippet 4
Lines 124-260

```HTML
@page {
	margin: 1in;
}

.collection-content {
	font-size: 0.875rem;
}

.column-list {
	display: flex;
	justify-content: space-between;
}

.column {
	padding: 0 1em;
}

.column:first-child {
	padding-left: 0;
}

.column:last-child {
	padding-right: 0;
}

.table_of_contents-item {
	display: block;
	font-size: 0.875rem;
	line-height: 1.3;
	padding: 0.125rem;
}

.table_of_contents-indent-1 {
	margin-left: 1.5rem;
}

.table_of_contents-indent-2 {
	margin-left: 3rem;
}

.table_of_contents-indent-3 {
	margin-left: 4.5rem;
}

.table_of_contents-link {
	text-decoration: none;
	opacity: 0.7;
	border-bottom: 1px solid rgba(55, 53, 47, 0.18);
}

table,
th,
td {
	border: 1px solid rgba(55, 53, 47, 0.09);
	border-collapse: collapse;
}

table {
	border-left: none;
	border-right: none;
}

th,
td {
	font-weight: normal;
	padding: 0.25em 0.5em;
	line-height: 1.5;
	min-height: 1.5em;
	text-align: left;
}

th {
	color: rgba(55, 53, 47, 0.6);
}

ol,
ul {
	margin: 0;
	margin-block-start: 0.6em;
	margin-block-end: 0.6em;
}

li > ol:first-child,
li > ul:first-child {
	margin-block-start: 0.6em;
}

ul > li {
	list-style: disc;
}

ul.to-do-list {
	padding-inline-start: 0;
}

ul.to-do-list > li {
	list-style: none;
}

.to-do-children-checked {
	text-decoration: line-through;
	opacity: 0.375;
}

ul.toggle > li {
	list-style: none;
}

ul {
	padding-inline-start: 1.7em;
}

ul > li {
	padding-left: 0.1em;
}

ol {
	padding-inline-start: 1.6em;
}

ol > li {
	padding-left: 0.2em;
}

.mono ol {
	padding-inline-start: 2em;
}

.mono ol > li {
	text-indent: -0.4em;
}

.toggle {
	padding-inline-start: 0em;
	list-style-type: none;
}
```

## Snippet 5
Lines 261-490

```HTML
/* Indent toggle children */
.toggle > li > details {
	padding-left: 1.7em;
}

.toggle > li > details > summary {
	margin-left: -1.1em;
}

.selected-value {
	display: inline-block;
	padding: 0 0.5em;
	background: rgba(206, 205, 202, 0.5);
	border-radius: 3px;
	margin-right: 0.5em;
	margin-top: 0.3em;
	margin-bottom: 0.3em;
	white-space: nowrap;
}

.collection-title {
	display: inline-block;
	margin-right: 1em;
}

.page-description {
	margin-bottom: 2em;
}

.simple-table {
	margin-top: 1em;
	font-size: 0.875rem;
	empty-cells: show;
}
.simple-table td {
	height: 29px;
	min-width: 120px;
}

.simple-table th {
	height: 29px;
	min-width: 120px;
}

.simple-table-header-color {
	background: rgb(247, 246, 243);
	color: black;
}
.simple-table-header {
	font-weight: 500;
}

time {
	opacity: 0.5;
}

.icon {
	display: inline-block;
	max-width: 1.2em;
	max-height: 1.2em;
	text-decoration: none;
	vertical-align: text-bottom;
	margin-right: 0.5em;
}

img.icon {
	border-radius: 3px;
}

.user-icon {
	width: 1.5em;
	height: 1.5em;
	border-radius: 100%;
	margin-right: 0.5rem;
}

.user-icon-inner {
	font-size: 0.8em;
}

.text-icon {
	border: 1px solid #000;
	text-align: center;
}

.page-cover-image {
	display: block;
	object-fit: cover;
	width: 100%;
	max-height: 30vh;
}

.page-header-icon {
	font-size: 3rem;
	margin-bottom: 1rem;
}

.page-header-icon-with-cover {
	margin-top: -0.72em;
	margin-left: 0.07em;
}

.page-header-icon img {
	border-radius: 3px;
}

.link-to-page {
	margin: 1em 0;
	padding: 0;
	border: none;
	font-weight: 500;
}

p > .user {
	opacity: 0.5;
}

td > .user,
td > time {
	white-space: nowrap;
}

input[type="checkbox"] {
	transform: scale(1.5);
	margin-right: 0.6em;
	vertical-align: middle;
}

p {
	margin-top: 0.5em;
	margin-bottom: 0.5em;
}

.image {
	border: none;
	margin: 1.5em 0;
	padding: 0;
	border-radius: 0;
	text-align: center;
}

.code,
code {
	background: rgba(135, 131, 120, 0.15);
	border-radius: 3px;
	padding: 0.2em 0.4em;
	border-radius: 3px;
	font-size: 85%;
	tab-size: 2;
}

code {
	color: #eb5757;
}

.code {
	padding: 1.5em 1em;
}

.code-wrap {
	white-space: pre-wrap;
	word-break: break-all;
}

.code > code {
	background: none;
	padding: 0;
	font-size: 100%;
	color: inherit;
}

blockquote {
	font-size: 1.25em;
	margin: 1em 0;
	padding-left: 1em;
	border-left: 3px solid rgb(55, 53, 47);
}

.bookmark {
	text-decoration: none;
	max-height: 8em;
	padding: 0;
	display: flex;
	width: 100%;
	align-items: stretch;
}

.bookmark-title {
	font-size: 0.85em;
	overflow: hidden;
	text-overflow: ellipsis;
	height: 1.75em;
	white-space: nowrap;
}

.bookmark-text {
	display: flex;
	flex-direction: column;
}

.bookmark-info {
	flex: 4 1 180px;
	padding: 12px 14px 14px;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
}

.bookmark-image {
	width: 33%;
	flex: 1 1 180px;
	display: block;
	position: relative;
	object-fit: cover;
	border-radius: 1px;
}

.bookmark-description {
	color: rgba(55, 53, 47, 0.6);
	font-size: 0.75em;
	overflow: hidden;
	max-height: 4.5em;
	word-break: break-word;
}

.bookmark-href {
	font-size: 0.75em;
	margin-top: 0.25em;
}
```

## Snippet 6
Lines 510-650

```HTML
.pdf:lang(ko-KR) .mono { font-family: PT Mono, iawriter-mono, Nitti, Menlo, Courier, monospace, 'Twemoji', 'Noto Color Emoji', 'Noto Sans Mono CJK KR'; }
.highlight-default {
	color: rgba(55, 53, 47, 1);
}
.highlight-gray {
	color: rgba(120, 119, 116, 1);
	fill: rgba(120, 119, 116, 1);
}
.highlight-brown {
	color: rgba(159, 107, 83, 1);
	fill: rgba(159, 107, 83, 1);
}
.highlight-orange {
	color: rgba(217, 115, 13, 1);
	fill: rgba(217, 115, 13, 1);
}
.highlight-yellow {
	color: rgba(203, 145, 47, 1);
	fill: rgba(203, 145, 47, 1);
}
.highlight-teal {
	color: rgba(68, 131, 97, 1);
	fill: rgba(68, 131, 97, 1);
}
.highlight-blue {
	color: rgba(51, 126, 169, 1);
	fill: rgba(51, 126, 169, 1);
}
.highlight-purple {
	color: rgba(144, 101, 176, 1);
	fill: rgba(144, 101, 176, 1);
}
.highlight-pink {
	color: rgba(193, 76, 138, 1);
	fill: rgba(193, 76, 138, 1);
}
.highlight-red {
	color: rgba(212, 76, 71, 1);
	fill: rgba(212, 76, 71, 1);
}
.highlight-default_background {
	color: rgba(55, 53, 47, 1);
}
.highlight-gray_background {
	background: rgba(248, 248, 247, 1);
}
.highlight-brown_background {
	background: rgba(244, 238, 238, 1);
}
.highlight-orange_background {
	background: rgba(251, 236, 221, 1);
}
.highlight-yellow_background {
	background: rgba(251, 243, 219, 1);
}
.highlight-teal_background {
	background: rgba(237, 243, 236, 1);
}
.highlight-blue_background {
	background: rgba(231, 243, 248, 1);
}
.highlight-purple_background {
	background: rgba(248, 243, 252, 1);
}
.highlight-pink_background {
	background: rgba(252, 241, 246, 1);
}
.highlight-red_background {
	background: rgba(253, 235, 236, 1);
}
.block-color-default {
	color: inherit;
	fill: inherit;
}
.block-color-gray {
	color: rgba(120, 119, 116, 1);
	fill: rgba(120, 119, 116, 1);
}
.block-color-brown {
	color: rgba(159, 107, 83, 1);
	fill: rgba(159, 107, 83, 1);
}
.block-color-orange {
	color: rgba(217, 115, 13, 1);
	fill: rgba(217, 115, 13, 1);
}
.block-color-yellow {
	color: rgba(203, 145, 47, 1);
	fill: rgba(203, 145, 47, 1);
}
.block-color-teal {
	color: rgba(68, 131, 97, 1);
	fill: rgba(68, 131, 97, 1);
}
.block-color-blue {
	color: rgba(51, 126, 169, 1);
	fill: rgba(51, 126, 169, 1);
}
.block-color-purple {
	color: rgba(144, 101, 176, 1);
	fill: rgba(144, 101, 176, 1);
}
.block-color-pink {
	color: rgba(193, 76, 138, 1);
	fill: rgba(193, 76, 138, 1);
}
.block-color-red {
	color: rgba(212, 76, 71, 1);
	fill: rgba(212, 76, 71, 1);
}
.block-color-default_background {
	color: inherit;
	fill: inherit;
}
.block-color-gray_background {
	background: rgba(248, 248, 247, 1);
}
.block-color-brown_background {
	background: rgba(244, 238, 238, 1);
}
.block-color-orange_background {
	background: rgba(251, 236, 221, 1);
}
.block-color-yellow_background {
	background: rgba(251, 243, 219, 1);
}
.block-color-teal_background {
	background: rgba(237, 243, 236, 1);
}
.block-color-blue_background {
	background: rgba(231, 243, 248, 1);
}
.block-color-purple_background {
	background: rgba(248, 243, 252, 1);
}
.block-color-pink_background {
	background: rgba(252, 241, 246, 1);
}
.block-color-red_background {
	background: rgba(253, 235, 236, 1);
}
```

## Snippet 7
Lines 664-686

```HTML
.select-value-color-washGlass { background-color: undefined; }

.checkbox {
	display: inline-flex;
	vertical-align: text-bottom;
	width: 16;
	height: 16;
	background-size: 16px;
	margin-left: 2px;
	margin-right: 5px;
}

.checkbox-on {
	background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%2216%22%20height%3D%2216%22%20viewBox%3D%220%200%2016%2016%22%20fill%3D%22none%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%0A%3Crect%20width%3D%2216%22%20height%3D%2216%22%20fill%3D%22%2358A9D7%22%2F%3E%0A%3Cpath%20d%3D%22M6.71429%2012.2852L14%204.9995L12.7143%203.71436L6.71429%209.71378L3.28571%206.2831L2%207.57092L6.71429%2012.2852Z%22%20fill%3D%22white%22%2F%3E%0A%3C%2Fsvg%3E");
}

.checkbox-off {
	background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%2216%22%20height%3D%2216%22%20viewBox%3D%220%200%2016%2016%22%20fill%3D%22none%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%0A%3Crect%20x%3D%220.75%22%20y%3D%220.75%22%20width%3D%2214.5%22%20height%3D%2214.5%22%20fill%3D%22white%22%20stroke%3D%22%2336352F%22%20stroke-width%3D%221.5%22%2F%3E%0A%3C%2Fsvg%3E");
}

</style></head><body><article id="60606a0c-1620-4eeb-93e0-a9d425280b90" class="page sans"><header><div class="page-header-icon undefined"><span class="icon">🔑</span></div><h1 class="page-title">API Keys and Codes</h1><p class="page-description"></p><table class="properties"><tbody></tbody></table></header><div class="page-body"><table id="28bbb7e2-ec5f-420d-85c0-099f0b429a5b" class="simple-table"><tbody><tr id="aec9f3ef-69fc-4535-9dbb-c66eaa66df08"><td id="woz{" class="" style="width:181px">SERVICE</td><td id="j`jJ" class="" style="width:809px">API KEY</td></tr><tr id="4086a5f4-389c-4363-befb-aaf5b5a001c4"><td id="woz{" class="" style="width:181px">AIR QUALITY OPEN DATA</td><td id="j`jJ" class="" style="width:809px">93eaf4ae2611e5c4576823656e0c82415633c077</td></tr><tr id="2d196106-d87f-4bae-8e79-21646211e68d"><td id="woz{" class="" style="width:181px">API2CONVERT</td><td id="j`jJ" class="" style="width:809px">607a4822657c3b44f786f1ea245d3f4a</td></tr><tr id="a08ddd9e-3c25-4026-8555-001b3213c3c6"><td id="woz{" class="" style="width:181px">CARBON MARKETPLACE</td><td id="j`jJ" class="" style="width:809px">VNfO2257BW0K4zEkCnKKdg</td></tr><tr id="29f14150-a632-4d13-948f-44f0ca0540c1"><td id="woz{" class="" style="width:181px">CAT</td><td id="j`jJ" class="" style="width:809px">live_9NYGtxVFC1gb9w2bjIpeZnBJDou6yE3r2PgpbEmfCp0Z43zRqv5nX0co48B6eLuc</td></tr><tr id="635e1fa6-b7d5-4abe-8aa7-402f9b486f94"><td id="woz{" class="" style="width:181px">COZE CALLBACK</td><td id="j`jJ" class="" style="width:809px"><a href="https://www.coze.com/auth/callback">https://www.coze.com/auth/callback</a></td></tr><tr id="232ee040-717c-479a-ad52-b89e490e26df"><td id="woz{" class="" style="width:181px">DATA.GOV</td><td id="j`jJ" class="" style="width:809px">vdfWjOKmgcQrXKlL6bxzipxPV3gtmQVFSoEKb2VX</td></tr><tr id="488eb932-e91d-4a7d-9cb1-d42afb404138"><td id="woz{" class="" style="width:181px">DDOWNLOAD</td><td id="j`jJ" class="" style="width:809px">405149o6axlnuvinkh129r</td></tr><tr id="b25ac59b-4a34-415c-9d01-2490f7795a44"><td id="woz{" class="" style="width:181px">DOG</td><td id="j`jJ" class="" style="width:809px">live_YQ3B7J7EJmAoFeZJWexRc8IllHUhGsfMAclMuf9uB007oF1T8fx0C8tG3637QctR</td></tr><tr id="430c359c-f73a-466a-920c-5793f4a9376f"><td id="woz{" class="" style="width:181px">DOMAIN NAME DISCOVERY</td><td id="j`jJ" class="" style="width:809px">PiHucpwCUfpA87dOUSWhqV0MJXQLBo89</td></tr><tr id="d59c79bf-2228-4798-8d37-1010b597bcd4"><td id="woz{" class="" style="width:181px">DROPBOX KEY</td><td id="j`jJ" class="" style="width:809px">628fi4lqggwydie</td></tr><tr id="fc1564e0-fb26-4548-9910-97e00c85f53c"><td id="woz{" class="" style="width:181px">DROPBOX SECRET</td><td id="j`jJ" class="" style="width:809px">xsggx99afqk29m9</td></tr><tr id="847ed66c-0bf6-416f-8379-e61724efb518"><td id="woz{" class="" style="width:181px">ELEVENLABS</td><td id="j`jJ" class="" style="width:809px">0ccf7f3237cd7c7b533d0c313ce73553</td></tr><tr id="8ffca5ed-ae19-4f01-a4b9-d9ea5001e715"><td id="woz{" class="" style="width:181px">EVENTBRITE</td><td id="j`jJ" class="" style="width:809px">FDG43MHVYS53GTZGIYGB</td></tr><tr id="e7229311-d070-4198-9c13-00fe2ab0db8a"><td id="woz{" class="" style="width:181px">FILE.IO</td><td id="j`jJ" class="" style="width:809px">RABUP7A.VWYAYFG-9YWMP4T-HPPTQTM-GFXQ17P</td></tr><tr id="ac92fba1-8c2f-44cf-bfca-7eb5535666ac"><td id="woz{" class="" style="width:181px">FOOTBALL DATA</td><td id="j`jJ" class="" style="width:809px">3f1bdd93fe424ac78f52173ac3bd9ea7</td></tr><tr id="91b8d50a-2e59-42da-b836-9c96ea93ed51"><td id="woz{" class="" style="width:181px">GEOCODE.MAPS.CO</td><td id="j`jJ" class="" style="width:809px">66be6044be017202539979xpl8d5b6b</td></tr><tr id="a8a95510-11a8-4bf3-873b-a4d2e1b90734"><td id="woz{" class="" style="width:181px">GEOSPY</td><td id="j`jJ" class="" style="width:809px">zpka_92f0f2ee6017414daffd69b74dd24568_652055a5</td></tr><tr id="4ccb15e4-2a56-4d70-a87a-ef70e06b5c7b"><td id="woz{" class="" style="width:181px">GOOGLE ANALYTICS</td><td id="j`jJ" class="" style="width:809px">G-2GE66JSNX1</td></tr><tr id="160a2c76-f642-80d6-b78a-dfc423c8db10"><td id="woz{" class="" style="width:181px">GOOGLE AI STUDIO</td><td id="j`jJ" class="" style="width:809px">AIzaSyDMrMcgVxmkA3xQs79TEkrZAz4ZWk8-Rms</td></tr><tr id="3ca18972-3129-4094-8764-bf7161ab77f9"><td id="woz{" class="" style="width:181px">GUARDIAN</td><td id="j`jJ" class="" style="width:809px">d4be32d-c296-430c-b599-3d223efb7df7</td></tr><tr id="b733b9e4-68fb-427a-95bd-e17f4a402487"><td id="woz{" class="" style="width:181px">HUME API KEY</td><td id="j`jJ" class="" style="width:809px">2znsmNukyTyNjMAzuA9tifmbFGcrgQ9HvqRFmj1lFxJqSOh5</td></tr><tr id="5629aee0-833e-4838-9dd5-0b4cd682bb4a"><td id="woz{" class="" style="width:181px">HUME SECRET KEY</td><td id="j`jJ" class="" style="width:809px">TNam2VFvufnAMVpO6QHKZzFZgVW3Vb7B6NRMGdSGdCcdUNA8JU9RGAWfNKQgBzaY</td></tr><tr id="35eb1ce1-17a7-4803-bb10-f339fec3439b"><td id="woz{" class="" style="width:181px">IMAGE UPLOAD API</td><td id="j`jJ" class="" style="width:809px">PiHucpwCUfpA87dOUSWhqV0MJXQLBo89</td></tr><tr id="b638c18f-44d8-4f7c-b704-42501b8e48eb"><td id="woz{" class="" style="width:181px">IMGBB</td><td id="j`jJ" class="" style="width:809px">a6bbdf2db4739180085dc678e0b707e9</td></tr><tr id="963f4181-6192-4eeb-8280-d2abffba7586"><td id="woz{" class="" style="width:181px">LITERAL</td><td id="j`jJ" class="" style="width:809px">lsk_UeYuMLlqb4ikynxnbQfPdN0Pjj6po83WBaH5sgGcbQI</td></tr><tr id="d944aca6-3aca-4af9-8896-f3c1aa78f530"><td id="woz{" class="" style="width:181px">LOGO.DEV</td><td id="j`jJ" class="" style="width:809px">pk_M0Yjc2CbT1iF0KaxQvrXAQ</td></tr><tr id="e9888f2b-5816-4b36-92e6-f5ab1d8f8126"><td id="woz{" class="" style="width:181px">LUPAN_KEY</td><td id="j`jJ" class="" style="width:809px">3df08e09-7d37-4377-bae9-98315b8be764</td></tr><tr id="6b205474-199b-40b5-b630-745c2c87f2cb"><td id="woz{" class="" style="width:181px">MAPQUEST</td><td id="j`jJ" class="" style="width:809px">857aMIxq4Ldp30Mi0MqABvsBjQijY5co</td></tr><tr id="fce69e29-b3b4-4a77-9be3-d2d0d9f70d88"><td id="woz{" class="" style="width:181px">MARKERAPI</td><td id="j`jJ" class="" style="width:809px">K3QNfyF2Z4</td></tr><tr id="16e1673f-34c1-47c8-a2c9-a2683118d513"><td id="woz{" class="" style="width:181px">MIRRIAM-WEBSTER LEARNERS DICTIONARY</td><td id="j`jJ" class="" style="width:809px">d035a35e-5b52-41ea-8823-47002751436b</td></tr><tr id="ea3292d2-a63a-4c15-a4f4-a48b128b128a"><td id="woz{" class="" style="width:181px">MIRRIAM-WEBSTER MEDICAL DICTIONARY</td><td id="j`jJ" class="" style="width:809px">a1ab4851-ebc1-4521-b6e6-5d0465aeec09</td></tr><tr id="9adff6b3-2411-46c9-8b39-4484abf7db03"><td id="woz{" class="" style="width:181px">NEWSAPI</td><td id="j`jJ" class="" style="width:809px">9024b98192924a96985b647f39ccb565</td></tr><tr id="b1b1b3aa-a744-4da3-9c17-f12f37432e2e"><td id="woz{" class="" style="width:181px">NUMBER VERIFICATION</td><td id="j`jJ" class="" style="width:809px">PiHucpwCUfpA87dOUSWhqV0MJXQLBo89</td></tr><tr id="204543ef-222a-498d-bc92-fd6ea76caba8"><td id="woz{" class="" style="width:181px">NYT</td><td id="j`jJ" class="" style="width:809px">vAU4TbbPTWlvQEzuvnbR6aAsoOqfe6Yc</td></tr><tr id="2e02a342-3d6b-416e-8f97-1613685e451a"><td id="woz{" class="" style="width:181px">NYT APP ID</td><td id="j`jJ" class="" style="width:809px">aa91ece9-1559-4c99-a69e-7ce1a284bb67</td></tr><tr id="ab53febd-209b-4841-8411-e23c60feb74c"><td id="woz{" class="" style="width:181px">OPENAI ASSISTED.SPACE TEST PROJECT</td><td id="j`jJ" class="" style="width:809px">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</td></tr><tr id="b078fd2d-102e-401b-89df-98f28c6c8fbd"><td id="woz{" class="" style="width:181px">OPENAI GMAIL ACCOUNT</td><td id="j`jJ" class="" style="width:809px">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</td></tr><tr id="113a2c76-f642-8050-acc7-e3d807f93997"><td id="woz{" class="" style="width:181px">OpenStates</td><td id="j`jJ" class="" style="width:809px">083f77a7-3f7a-49bf-ac44-d92047b7902a<br/><br/></td></tr><tr id="e7139d77-1db7-4ff8-a93d-5a1f53efe051"><td id="woz{" class="" style="width:181px">PEXELS</td><td id="j`jJ" class="" style="width:809px">GgT201e3UcbOyt9aMO9iAyei38XiriD8EG4YgR9DxbytEPPMwCkiPxl1</td></tr><tr id="17edaafd-c840-44c2-9930-ddbc6f667f68"><td id="woz{" class="" style="width:181px">PINECONE</td><td id="j`jJ" class="" style="width:809px">d040d4ba-db16-4766-af46-c680c35f911a</td></tr><tr id="a9c7e6d4-f91c-4c34-ad08-da51af842c30"><td id="woz{" class="" style="width:181px">PIXABAY</td><td id="j`jJ" class="" style="width:809px">45497543-be9605f4a10e5812fff3aa61f</td></tr><tr id="7f85859a-3a74-46c9-b2cc-d448ab12d875"><td id="woz{" class="" style="width:181px">REDDIT CLIENT ID</td><td id="j`jJ" class="" style="width:809px"><strong>yeR_uWe8pr8fCd53IF7EOA</strong></td></tr><tr id="fffa2c76-f642-8026-9533-eba60df63516"><td id="woz{" class="" style="width:181px">REDDIT SECRET</td><td id="j`jJ" class="" style="width:809px">-UY8hWNP5N_0zjpmyKQa3pOZyDh0tQ</td></tr><tr id="2eebe718-37ff-42dd-83ae-0f4cf67b7b00"><td id="woz{" class="" style="width:181px">SCRAPESTACK</td><td id="j`jJ" class="" style="width:809px">141991d2b4d9784c24f5ec7b2ecb261a</td></tr><tr id="2b32af68-4742-4186-b928-eb0ea430e89f"><td id="woz{" class="" style="width:181px">SKILLS</td><td id="j`jJ" class="" style="width:809px">PiHucpwCUfpA87dOUSWhqV0MJXQLBo89</td></tr><tr id="fffa2c76-f642-801e-baee-f7237866f941"><td id="woz{" class="" style="width:181px">SPOONTACULAR</td><td id="j`jJ" class="" style="width:809px">PiHucpwCUfpA87dOUSWhqV0MJXQLBo89</td></tr><tr id="45af3401-739a-4703-8b94-a89e1244bd2c"><td id="woz{" class="" style="width:181px">TAX DATA</td><td id="j`jJ" class="" style="width:809px">PiHucpwCUfpA87dOUSWhqV0MJXQLBo89</td></tr><tr id="a532e513-0720-4329-8158-0cf4cc31901f"><td id="woz{" class="" style="width:181px">TELEGRAPH</td><td id="j`jJ" class="" style="width:809px">36aae5a265aaa60403b5042a9c648cc787032353c7f02bad525bcddedbd2</td></tr><tr id="22eb3083-814f-490b-882f-c99350ae9b34"><td id="woz{" class="" style="width:181px">TELEGRAPH URL</td><td id="j`jJ" class="" style="width:809px">/coolhand</td></tr><tr id="dd6e4ee2-cd2d-4701-aa78-f06f01071743"><td id="woz{" class="" style="width:181px">TISANE PRIMARY</td><td id="j`jJ" class="" style="width:809px">Primary Key: 52573597091145c2befcc184c54b49ff Hide | Regenerate</td></tr><tr id="e07a4993-fcdc-472e-ae11-639ea59e8739"><td id="woz{" class="" style="width:181px">TISANE SECONDARY</td><td id="j`jJ" class="" style="width:809px">8b68016eea87407783264fe767362e76<a href="https://docs.tisane.ai/">https://docs.tisane.ai/</a></td></tr><tr id="c52cd38d-57cf-4bcc-9432-8368f38f2e2f"><td id="woz{" class="" style="width:181px">TWILIO SENDGRID</td><td id="j`jJ" class="" style="width:809px">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</td></tr><tr id="f5aa9af9-10b8-42e4-b084-a61874cfa587"><td id="woz{" class="" style="width:181px">WALK SCORE</td><td id="j`jJ" class="" style="width:809px">61b0834f61254d3dab14e9683a592c7b</td></tr><tr id="417684be-ed4c-4c96-9dab-dee6d6b7c216"><td id="woz{" class="" style="width:181px">WINDY WEBCAMS</td><td id="j`jJ" class="" style="width:809px">oEr5iOwUmtblbu9prTMVQBTilkIVlr2j</td></tr><tr id="36e3206c-0821-41f6-9052-51e1dc847880"><td id="woz{" class="" style="width:181px">ZENSCRAPE</td><td id="j`jJ" class="" style="width:809px">d5422ce0-45a0-11ef-afd9-eb0b1bd98310</td></tr><tr id="ade67de8-bb3c-4dda-9c5c-f847b6ac2181"><td id="woz{" class="" style="width:181px">box client id</td><td id="j`jJ" class="" style="width:809px">ea88pgjg8e1zt2i07dwo2b9hqvep4m8w</td></tr><tr id="62b275e2-2ec3-4ee5-bdcd-1bf2bbc51de8"><td id="woz{" class="" style="width:181px">box client secret</td><td id="j`jJ" class="" style="width:809px">qmgDTW7QETgEAOBcIWKn2Y3C7VtcRaBl</td></tr><tr id="916b5058-17f8-4934-9625-67d7297271c3"><td id="woz{" class="" style="width:181px">box redirect uri</td><td id="j`jJ" class="" style="width:809px"></td></tr><tr id="fee344f0-cd49-45fd-b8e2-ae98a337407f"><td id="woz{" class="" style="width:181px">box developer token</td><td id="j`jJ" class="" style="width:809px">YP54MbTrIz5rzD34zwBcLtKPt9ObNIba</td></tr><tr id="ae27287c-8bf0-4ecd-bb63-44f82bffd9ec"><td id="woz{" class="" style="width:181px">catbox userhash</td><td id="j`jJ" class="" style="width:809px">7142be6a53f25128cde43a20b</td></tr><tr id="fffa2c76-f642-8077-903b-f4cf921ea881"><td id="woz{" class="" style="width:181px">Court Listener</td><td id="j`jJ" class="" style="width:809px">792807e28e4c87a6ad9f26ad33f63f89bd345848<br/><br/></td></tr><tr id="c0f28a71-87b8-48c5-bdb8-ac9935065ae0"><td id="woz{" class="" style="width:181px">coze oauth client secret</td><td id="j`jJ" class="" style="width:809px">m01RCcioZBsrL9fITMvdKqbkcupS5NjAGQ6MJGqiRMk92V6a<br/><br/></td></tr><tr id="be4ec023-bce9-4230-9be1-f50a83d9ee49"><td id="woz{" class="" style="width:181px">coze oauth client id</td><td id="j`jJ" class="" style="width:809px">62592026224476764172210035870613.app.coze</td></tr><tr id="8ece09d0-d80f-4551-bb41-3411a0bfea4f"><td id="woz{" class="" style="width:181px">public key</td><td id="j`jJ" class="" style="width:809px">eG-93FCA1BdSBqjLGouqa63XyLkPC2pJu3hyh7Zt76o</td></tr><tr id="39a5e592-5ead-4afa-ae97-48f9c6dca7ce"><td id="woz{" class="" style="width:181px">perplexity</td><td id="j`jJ" class="" style="width:809px">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</td></tr><tr id="10aa2c76-f642-8030-9efe-fd2e0bba9765"><td id="woz{" class="" style="width:181px">noun project key</td><td id="j`jJ" class="" style="width:809px">ec09e88b27844163951f33ecc1b2dc38</td></tr><tr id="10aa2c76-f642-80ca-b225-cc081f9af5e4"><td id="woz{" class="" style="width:181px">noun project secret</td><td id="j`jJ" class="" style="width:809px">1aabda8cb9404568a3d06f34508b604c</td></tr><tr id="10da2c76-f642-8072-bf5a-e8b4912f75de"><td id="woz{" class="" style="width:181px">google ai studio</td><td id="j`jJ" class="" style="width:809px">AIzaSyDZXYJiDcXQNr3yPh8hjgIfglQFp5ED-os</td></tr><tr id="10ea2c76-f642-80df-b1bd-fea066e81f68"><td id="woz{" class="" style="width:181px">fish audio</td><td id="j`jJ" class="" style="width:809px">05860ac7d27f4900900ef28f77bf81de</td></tr><tr id="114a2c76-f642-8058-9b02-f8cc7270f83a"><td id="woz{" class="" style="width:181px">telegram public key</td><td id="j`jJ" class="" style="width:809px">MIIBCgKCAQEAyMEdY1aR+sCR3ZSJrtztKTKqigvO/vBfqACJLZtS7QMgCGXJ6XIR<br/>yy7mx66W0/sOFa7/1mAZtEoIokDP3ShoqF4fVNb6XeqgQfaUHd8wJpDWHcR2OFwv<br/>plUUI1PLTktZ9uW2WE23b+ixNwJjJGwBDJPQEQFBE+vfmH0JP503wr5INS1poWg/<br/>j25sIWeYPHYeOrFp/eXaqhISP6G+q2IeTaWTXpwZj4LzXq5YOpk4bYEQ6mvRq7D1<br/>aHWfYmlEGepfaYR8Q0YqvvhYtMte3ITnuSJs171+GDqpdKcSwHnd6FudwGO4pcCO<br/>j4WcDuXc2CTHgH8gFTNhp/Y8/SpDOhvn9QIDAQAB<br/><br/></td></tr><tr id="114a2c76-f642-801a-9034-c47571fed9f1"><td id="woz{" class="" style="width:181px">telegram app hash</td><td id="j`jJ" class="" style="width:809px">6bbbc3ba6fc03f1d2d2e419ae985abc2<br/><br/></td></tr><tr id="114a2c76-f642-80ae-b45f-ee43c3276f46"><td id="woz{" class="" style="width:181px">telegram app id</td><td id="j`jJ" class="" style="width:809px"><strong>20471525</strong></td></tr><tr id="119a2c76-f642-805d-b8ef-e1f17ac740e6"><td id="woz{" class="" style="width:181px">Coze 2 10-7-24</td><td id="j`jJ" class="" style="width:809px">pat_JF8Lre4IgXOABlmf383x7GyLF6cj6yn6E4ElRKtvYP3DXpYmB9gJpoMyw2qfwjX4</td></tr><tr id="12aa2c76-f642-80b8-badd-ee04f0ce0c3c"><td id="woz{" class="" style="width:181px">ngrok</td><td id="j`jJ" class="" style="width:809px">2nwi0pAMNU7gsbRCLorllMFZMh6_6vxMebfopmf2PiG31Wi92ngrok</td></tr><tr id="12aa2c76-f642-8055-90a2-ed92dde0d29d"><td id="woz{" class="" style="width:181px">ngrok</td><td id="j`jJ" class="" style="width:809px">2nwjSVkODNqPq9zmcTli6jMb2fQ_3fXk8v1qQS6E7EDqH1Kip</td></tr><tr id="145a2c76-f642-80c6-8301-c74c89ee0d07"><td id="woz{" class="" style="width:181px">huggingface</td><td id="j`jJ" class="" style="width:809px">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</td></tr><tr id="145a2c76-f642-8037-9022-fc3a8c8bfae0"><td id="woz{" class="" style="width:181px">Mistral</td><td id="j`jJ" class="" style="width:809px">n8R347515VqP48oDHwBeL9BS6nW1L8zY</td></tr><tr id="145a2c76-f642-80ff-86f2-e8f7640131a4"><td id="woz{" class="" style="width:181px">REBRANDLY</td><td id="j`jJ" class="" style="width:809px">fa20342750ef4605b1fcde7988b35088</td></tr><tr id="145a2c76-f642-80fc-8b34-c24fbc11028c"><td id="woz{" class="" style="width:181px">GIT PERSONAL ACCESS TOKEN</td><td id="j`jJ" class="" style="width:809px">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</td></tr><tr id="145a2c76-f642-800e-bc07-d27f7eb79149"><td id="woz{" class="" style="width:181px">GIT CLASSIC TOKEN</td><td id="j`jJ" class="" style="width:809px">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</td></tr><tr id="145a2c76-f642-8040-8a5a-d41c4a8f4395"><td id="woz{" class="" style="width:181px">Coze</td><td id="j`jJ" class="" style="width:809px">pat_NWdh5zaCuFIx1FfUg78aNCEskA2FlqQ1KpoAQbc7I4L3HNYSjbBelPGs5VM87n5v</td></tr><tr id="145a2c76-f642-80b6-a159-e4a712b7234d"><td id="woz{" class="" style="width:181px">Anthropic</td><td id="j`jJ" class="" style="width:809px">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</td></tr><tr id="146a2c76-f642-8035-b466-f7860d70c29f"><td id="woz{" class="" style="width:181px">POSTMAN VAULT</td><td id="j`jJ" class="" style="width:809px">fb47ad27500f41ee00a25fcdb38338c1840052ea7126b1a414fd17949979a487</td></tr><tr id="167a2c76-f642-8060-a179-e18f468c1f7c"><td id="woz{" class="" style="width:181px">Github Useful Org Token</td><td id="j`jJ" class="" style="width:809px">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</td></tr></tbody></table><p id="181a2c76-f642-8028-8937-fcb8f70250b0" class="">NEW HF INFERENCE - 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</p><p id="17ea2c76-f642-80d1-891b-cbbc39a02dc0" class="">COZETHROUGH 2-16: pat_z9m6SrGlSPUmYp1VByhg3pAWCHT8seWt4taZmhAaimRCXMR9qtxMRDgs9B1RsnnD</p><p id="182a2c76-f642-8083-9537-ec47217aab1d" class="">COHERE: g6KjvSLHSTOZv7E6Y749YYpOO1gc3pmbVqW0x0DJ</p><p id="182a2c76-f642-80cb-856f-c81a7721df88" class="">Coze made Jan 21 - pat_Uk4Z075Oo8RE5Po13rBUoEQNzr3dcKTNmBuf5Qtj1V6QZLiwAeZDaNzfNSLMIca8</p><figure id="146a2c76-f642-8089-9382-ef1be8a24fb7" class="image"><a href="API%20Keys%20and%20Codes%2060606a0c16204eeb93e0a9d425280b90/CleanShot_2024-11-21_at_16.17.04.png"><img style="width:1162.9947509765625px" src="API%20Keys%20and%20Codes%2060606a0c16204eeb93e0a9d425280b90/CleanShot_2024-11-21_at_16.17.04.png"/></a></figure><p id="17ea2c76-f642-8038-a4fa-ce66710a36fe" class="">
</p><p id="17ea2c76-f642-805c-b53e-f604eab93935" class="">
</p><p id="17ea2c76-f642-8083-91d2-c655cbfef22c" class="">
```

