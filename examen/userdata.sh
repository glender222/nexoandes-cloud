#!/bin/bash
dnf update -y
dnf install -y httpd
systemctl enable httpd
systemctl start httpd

cat << 'HTML' > /var/www/html/index.html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EXAMEN CLOUD COMPUTING</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f0f4f8;
      color: #232f3e;
      margin: 0;
      padding: 40px 20px;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 80vh;
    }
    .card {
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
      max-width: 650px;
      width: 100%;
      padding: 40px;
      border-top: 6px solid #ff9900;
    }
    h1 {
      color: #1a2530;
      font-size: 26px;
      margin-top: 0;
      margin-bottom: 12px;
      border-bottom: 2px solid #eaeded;
      padding-bottom: 12px;
    }
    .badge {
      display: inline-block;
      background-color: #0073bb;
      color: #ffffff;
      padding: 6px 14px;
      border-radius: 20px;
      font-weight: 600;
      font-size: 14px;
      margin-bottom: 20px;
    }
    .info-group {
      margin: 14px 0;
      font-size: 16px;
      line-height: 1.6;
    }
    .info-label {
      font-weight: 700;
      color: #555;
      display: inline-block;
      width: 190px;
    }
    .info-value {
      color: #111;
      font-weight: 600;
    }
    .footer {
      margin-top: 30px;
      padding-top: 15px;
      border-top: 1px dashed #d5dbdb;
      font-size: 13px;
      color: #767676;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>EXAMEN CLOUD COMPUTING</h1>
    <div class="badge">Servidor implementado en AWS</div>
    <div class="info-group">
      <span class="info-label">Estudiante:</span>
      <span class="info-value">Glender Vargas</span>
    </div>
    <div class="info-group">
      <span class="info-label">Caso de evaluación:</span>
      <span class="info-value">InnovaTech Perú &mdash; Servidor Web Linux</span>
    </div>
    <div class="info-group">
      <span class="info-label">Docente:</span>
      <span class="info-value">Asin Gomez Fernando Manuel</span>
    </div>
    <div class="info-group">
      <span class="info-label">Fecha:</span>
      <span class="info-value">22 / 10 / 2026</span>
    </div>
    <div class="info-group">
      <span class="info-label">Plataforma:</span>
      <span class="info-value">AWS Academy Learner Lab (Amazon Linux 2023)</span>
    </div>
    <div class="footer">
      Servidor Apache HTTPD activo &bull; Puerto 80 &bull; Arquitectura VPC propia
    </div>
  </div>
</body>
</html>
HTML
