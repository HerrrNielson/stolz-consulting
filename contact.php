<?php
/**
 * Stolz Consulting – Kontaktformular-Handler
 * Versendet die Anfrage per mail() an die unten hinterlegte Adresse.
 * Voraussetzung: PHP-Hosting mit funktionierendem Mailversand (noch auf dem Zielserver zu testen).
 *
 * - Antwort immer als JSON: {"ok": true|false, "code": "...", "message": "..."} – "message" in der
 *   Sprache des Formulars (de/en/fr/ru). Die Website-Texte stehen zusätzlich in i18n/<sprache>.py.
 * - Pflichtfelder: name, email, message, consent. Honeypot-Feld: "website" (muss leer bleiben).
 * - Header-Injection: Zeilenumbrüche in Name/E-Mail/Betreff führen zur Ablehnung; im Mail-Header
 *   stehen nur feste Werte bzw. die validierte E-Mail-Adresse.
 * - Orientierungs-Check (Popup, assets/js/analyse.js): gleiche Felder plus source=analyse, analyse_topics
 *   (kommagetrennte IDs), analyse_phase, analyse_size. Die Nachricht ist dort optional. IDs werden nur über
 *   die Whitelists unten in Klartext (Deutsch) für die Mail übersetzt; unbekannte Werte werden ignoriert.
 * RECHTLICH/DATENSCHUTZ: von Fachperson zu prüfen (Einwilligungsnachweis, Speicherdauer der Mails).
 */

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

const RECIPIENT = 'office@stolz-consulting.net';
const FROM      = 'no-reply@stolz-consulting.net';

const MESSAGES = [
    'de' => [
        'ok'      => 'Vielen Dank, Ihre Nachricht ist bei mir eingegangen.',
        'invalid' => 'Bitte füllen Sie alle Pflichtfelder aus, geben Sie eine gültige E-Mail-Adresse an und bestätigen Sie die Datenschutzerklärung.',
        'error'   => 'Die Nachricht konnte leider nicht gesendet werden. Bitte versuchen Sie es später noch einmal oder schreiben Sie direkt an office@stolz-consulting.net.',
    ],
    'en' => [
        'ok'      => 'Thank you, your message has reached me.',
        'invalid' => 'Please fill in all required fields, enter a valid email address and confirm the privacy policy.',
        'error'   => 'Unfortunately, your message could not be sent. Please try again later or write directly to office@stolz-consulting.net.',
    ],
    'fr' => [
        'ok'      => "Merci, votre message m’est bien parvenu.",
        'invalid' => "Veuillez remplir tous les champs obligatoires, indiquer une adresse e-mail valide et confirmer la politique de confidentialité.",
        'error'   => "Votre message n’a malheureusement pas pu être envoyé. Veuillez réessayer plus tard ou écrire directement à office@stolz-consulting.net.",
    ],
    'ru' => [
        'ok'      => 'Благодарю Вас, Ваше сообщение получено.',
        'invalid' => 'Пожалуйста, заполните все обязательные поля, укажите действительный адрес электронной почты и подтвердите политику конфиденциальности.',
        'error'   => 'К сожалению, сообщение не удалось отправить. Пожалуйста, повторите попытку позже или напишите напрямую на office@stolz-consulting.net.',
    ],
];

// Orientierungs-Check: erlaubte IDs -> Klartext für die Mail an die Beraterin (immer Deutsch)
const ANALYSE_TOPICS = [
    'controlling'   => 'Controlling und Finanzsteuerung',
    'finanzierung'  => 'Finanzierung',
    'international' => 'Wachstum und Internationalisierung',
    'erp'           => 'ERP und IT-Prozesse',
    'training'      => 'Schulung und Training',
    'unklar'        => 'Noch unklar',
];
const ANALYSE_PHASES = [
    'plan'   => 'Plant noch',
    'act'    => 'Konkreter Handlungsbedarf',
    'second' => 'Sucht eine zweite Meinung',
    'first'  => 'Wünscht eine erste Einordnung',
    'info'   => 'Möchte sich zunächst informieren',
];
const ANALYSE_SIZES = [
    'micro' => 'Kleinstunternehmen',
    'sme'   => 'KMU bis 50 Mitarbeitende',
    'large' => 'Größeres Unternehmen',
];

function respond(int $status, bool $ok, string $code, string $lang): void {
    http_response_code($status);
    $key = $ok ? 'ok' : ($code === 'invalid' ? 'invalid' : 'error');
    echo json_encode(['ok' => $ok, 'code' => $code, 'message' => MESSAGES[$lang][$key]], JSON_UNESCAPED_UNICODE);
    exit;
}

function field(string $key, int $max = 500): string {
    $v = $_POST[$key] ?? '';
    if (!is_string($v)) {
        return '';
    }
    $v = trim(str_replace("\0", '', $v));
    return mb_substr($v, 0, $max);
}

$rawLang = field('lang', 2);
$lang    = array_key_exists($rawLang, MESSAGES) ? $rawLang : 'de';

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    respond(405, false, 'method', $lang);
}

// Honeypot gegen Spam-Bots: scheinbarer Erfolg, es wird nichts versendet
if (field('website', 200) !== '') {
    respond(200, true, 'ok', $lang);
}

$name    = field('name', 120);
$company = field('company', 160);
$email   = field('email', 160);
$phone   = field('phone', 60);
$subject = field('subject', 160);
$message = field('message', 5000);
$consent = field('consent', 5) !== '';
$analyse = field('source', 20) === 'analyse';

// Header-Injection: einzeilige Felder dürfen keine Zeilenumbrüche enthalten -> ablehnen
foreach ([$name, $company, $email, $phone, $subject] as $single) {
    if (preg_match('/[\r\n]/', $single)) {
        respond(422, false, 'invalid', $lang);
    }
}

// Beim Orientierungs-Check ist die Nachricht optional
if ($name === '' || ($message === '' && !$analyse) || !$consent || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    respond(422, false, 'invalid', $lang);
}

$topics = [];
if ($analyse) {
    foreach (explode(',', field('analyse_topics', 120)) as $id) {
        if (isset(ANALYSE_TOPICS[$id]) && !in_array(ANALYSE_TOPICS[$id], $topics, true)) {
            $topics[] = ANALYSE_TOPICS[$id];
        }
    }
    $phase = ANALYSE_PHASES[field('analyse_phase', 20)] ?? '-';
    $size  = ANALYSE_SIZES[field('analyse_size', 20)] ?? '-';
    $subject = 'Orientierungsgespräch (Orientierungs-Check)';
}

$mailSubject = 'Website-Anfrage' . ($subject !== '' ? ': ' . $subject : '') . ' (' . strtoupper($lang) . ')';

$body  = "Neue Anfrage über stolz-consulting.net\n\n";
$body .= "Name:        $name\n";
$body .= "Unternehmen: " . ($company !== '' ? $company : '-') . "\n";
$body .= "E-Mail:      $email\n";
$body .= "Telefon:     " . ($phone !== '' ? $phone : '-') . "\n";
$body .= "Sprache:     " . strtoupper($lang) . "\n";
$body .= "Einwilligung Datenschutzerklärung: ja (" . date('Y-m-d H:i:s T') . ")\n\n";
if ($analyse) {
    $body .= "--- Orientierungs-Check (Angaben des Besuchers) ---\n";
    $body .= "Thema(en):    " . ($topics ? implode('; ', $topics) : '-') . "\n";
    $body .= "Situation:    $phase\n";
    $body .= "Größe:        $size\n";
    $body .= "Wunsch:       unverbindliches Orientierungsgespräch\n\n";
}
$body .= "Nachricht:\n" . ($message !== '' ? $message : '-') . "\n";

$headers = [
    'From: Stolz Consulting Website <' . FROM . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=utf-8',
    'X-Mailer: PHP/' . phpversion(),
];

$sent = mail(
    RECIPIENT,
    '=?UTF-8?B?' . base64_encode($mailSubject) . '?=',
    $body,
    implode("\r\n", $headers)
);

if ($sent) {
    respond(200, true, 'ok', $lang);
}
respond(500, false, 'send', $lang);
