# DDC RVT converter, Linux x86-64 command line.
#   docker build -t ddc-rvt-converter integrations/docker
#   docker run --rm -v "$PWD:/data" ddc-rvt-converter /data/model.rvt --xlsx --gltf --out /data/out
FROM ubuntu:22.04

ARG DDC_VERSION=2.0.5

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

# Download and verify against the release checksums.
RUN set -eux; \
    base="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v${DDC_VERSION}"; \
    pkg="DDC-RVT-Converter-${DDC_VERSION}-linux-x64.tar.gz"; \
    curl -fsSL -o "/tmp/${pkg}" "${base}/${pkg}"; \
    curl -fsSL -o /tmp/SHA256SUMS.txt "${base}/SHA256SUMS.txt"; \
    (cd /tmp && grep " \*\?${pkg}\$" SHA256SUMS.txt | sha256sum -c -); \
    tar -xzf "/tmp/${pkg}" -C /opt; \
    ln -s /opt/rvt-decode-linux-x64/rvt-decode /usr/local/bin/rvt-decode; \
    rm -f /tmp/*.tar.gz /tmp/SHA256SUMS.txt

WORKDIR /data
ENTRYPOINT ["rvt-decode"]
CMD ["--help"]
