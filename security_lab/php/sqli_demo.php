<?php
declare(strict_types=1);
// Demonstration of the defensive pattern: parameterized queries.
// Run only on localhost with a disposable training database.
$message = 'استخدم الاستعلامات المعلّمة بدلاً من دمج مدخلات المستخدم داخل SQL.';
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"><title>منع SQL Injection</title></head>
<body>
<h1>تجربة منع SQL Injection</h1>
<p><?= htmlspecialchars($message, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') ?></p>
<pre>$stmt = $pdo->prepare('SELECT * FROM demo_users WHERE username = :username');
$stmt->execute(['username' => $username]);</pre>
</body></html>
