# Compilation de l'application Flutter pour le web, puis service par
# nginx. L'image finale ne contient que des fichiers statiques : ni le
# SDK Flutter, ni les sources.

FROM debian:bookworm-slim AS compilation

ARG FLUTTER_VERSION=3.47.4
# Adresse de l'API telle que le NAVIGATEUR la joindra. Injectée à la
# compilation : une seule image sert donc un environnement donné, et
# aucun code conditionnel ne traîne dans l'application.
ARG API_BASE=/api

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates git unzip xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL -o /tmp/flutter.tar.xz \
      "https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_${FLUTTER_VERSION}-stable.tar.xz" \
    && tar xf /tmp/flutter.tar.xz -C /opt \
    && rm /tmp/flutter.tar.xz \
    && git config --global --add safe.directory /opt/flutter
ENV PATH="/opt/flutter/bin:${PATH}"
# Sans cela, chaque commande tente de joindre Google Analytics et
# noircit le journal de compilation d'un paragraphe sur la vie privée.
ENV FLUTTER_SUPPRESS_ANALYTICS=true

WORKDIR /source
# Les dépendances d'abord : une modification du code ne refait pas
# cette étape. Les traductions viennent AVEC, parce que « pub get »
# génère le code de localisation et échoue si lib/l10n n'existe pas
# encore — c'est ce qui cassait la construction.
COPY pubspec.yaml pubspec.lock l10n.yaml ./
COPY lib/l10n ./lib/l10n
RUN flutter pub get

COPY . .
# --no-web-resources-cdn embarque CanvasKit dans l'image au lieu de le
# charger depuis gstatic.com, qu'un réseau d'établissement filtre
# parfois — et qui laisserait une page blanche sans le moindre message.
RUN flutter build web --release --no-web-resources-cdn \
        --dart-define=API_BASE="${API_BASE}"

FROM nginx:alpine
COPY --from=compilation /source/build/web /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
