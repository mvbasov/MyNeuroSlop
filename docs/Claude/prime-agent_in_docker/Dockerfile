# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Prime Agent — Alpine Linux container image
#
# Runs `prime-agent` (the Prime Intellect RLM-native coding agent CLI) from
# an Alpine base. Mount any host folder(s) into the container and
# prime-agent will operate on them via its IPython tool.
#
# Build:
#   docker build -t prime-agent .
#
# Run (mount current directory as /workspace, persist agent config/auth):
#   docker run -it --rm \
#     -v "$PWD":/workspace \
#     -v prime-agent-config:/home/agent/.prime \
#     -w /workspace \
#     prime-agent
#
# Mount additional folders as needed, e.g.:
#   docker run -it --rm \
#     -v "$PWD":/workspace \
#     -v /path/on/host/other-project:/mnt/other-project \
#     -v prime-agent-config:/home/agent/.prime \
#     -w /workspace \
#     prime-agent
#
# Pass API keys via env, e.g.:
#   docker run -it --rm -e ANTHROPIC_API_KEY=sk-ant-... -v "$PWD":/workspace prime-agent
#
# Pin a specific release instead of "stable":
#   docker build --build-arg PRIME_AGENT_VERSION=0.7.1 -t prime-agent .
#
# --- System-wide proxychains, using your EXISTING host proxychains setup ---
# The image ships LD_PRELOAD=/usr/lib/libproxychains4.so and
# PROXYCHAINS_CONF_FILE=/etc/proxychains.conf (same as the host). At run
# time, bind-mount the host's real config in read-only and share the host's
# network namespace so proxy entries like "http 127.0.0.1 10809" resolve to
# the actual local proxy already running on the host:
#
#   docker run -it --rm \
#     --network host \
#     -v /etc/proxychains.conf:/etc/proxychains.conf:ro \
#     -v "$PWD":/workspace \
#     -v prime-agent-config:/home/agent/.prime \
#     -w /workspace \
#     prime-agent
#
# Every process in the container — prime-agent's own network calls, git,
# curl, and any `docker build`/`buildx` invoked from the agent's ipython
# tool — is now transparently routed through your existing proxychains
# config, with zero image rebuilds if that config later changes.
#
# --- Docker-outside-of-Docker: let the agent trigger (parallel) host builds ---
# Mount the host's Docker socket (and matching CLI, already installed in
# this image) so `docker build`/`docker buildx bake` invoked by the agent's
# ipython tool run against the HOST's Docker daemon, sibling to this
# container, instead of needing a nested dockerd:
#
#   docker run -it --rm \
#     --network host \
#     -v /etc/proxychains.conf:/etc/proxychains.conf:ro \
#     -v "$PWD":/workspace \
#     -v /var/run/docker.sock:/var/run/docker.sock \
#     --group-add "$(stat -c '%g' /var/run/docker.sock)" \
#     -v prime-agent-config:/home/agent/.prime \
#     -w /workspace \
#     prime-agent
#
# Inside the container, the agent can now kick off N project builds in
# parallel (each already wrapped in the same system-wide proxychains via
# LD_PRELOAD, so pulls/pushes go through your proxy):
#
#   ls */Dockerfile | xargs -P 4 -I{} sh -c '
#     dir=$(dirname "{}");
#     docker build -t "$(basename "$dir")":latest "$dir"
#   '
#
# or with GNU parallel (already installed in this image):
#
#   parallel --jobs 4 docker build -t {/}:latest {} ::: proj-a proj-b proj-c
#
# or via a single buildx bake file describing all targets:
#
#   docker buildx bake -f docker-bake.hcl
# ---------------------------------------------------------------------------

FROM alpine:3.21

# Runtime deps:
#   - nodejs/npm: prime-agent CLI runtime (Node.js >= 22.8.0)
#   - bash: %%bash tool cells and general shell usage
#   - python3/py3-pip: IPython kernel backing the "ipython" tool
#   - curl, ca-certificates: fetching release artifacts + general network use
#   - git: repo operations from the agent
#   - build-base, libffi-dev, openssl-dev: native/pip build fallbacks
RUN apk add --no-cache \
        nodejs \
        npm \
        bash \
        curl \
        ca-certificates \
        git \
        python3 \
        py3-pip \
        build-base \
        libffi-dev \
        openssl-dev \
        proxychains-ng \
        docker-cli \
        docker-cli-buildx \
        parallel \
        ripgrep \
        shadow \
    && rm -rf /var/cache/apk/*

# Install uv (manages the Python kernel venv prime-agent's ipython tool uses)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Create a non-root user to run the agent, with a home directory for
# ~/.prime/agent (config, auth, sessions) and a default workspace mount.
# Also create a "docker" group placeholder: at `docker run` time, mount the
# host's /var/run/docker.sock and pass `--group-add $(stat -c '%g'
# /var/run/docker.sock)` so `agent` can talk to the host Docker daemon
# (Docker-outside-of-Docker) without running a nested dockerd.
ARG AGENT_UID=1000
ARG AGENT_GID=1000
RUN addgroup -g "$AGENT_GID" agent \
    && adduser -D -u "$AGENT_UID" -G agent -h /home/agent -s /bin/bash agent \
    && addgroup docker \
    && adduser agent docker \
    && mkdir -p /workspace \
    && chown -R agent:agent /home/agent /workspace

# Install Prime Agent globally as root (writes into /usr/lib/node_modules),
# fetching the versioned release tarball directly from the release CDN
# (the same artifact https://app.primeintellect.ai/prime-agent/install.sh
# resolves and installs, without requiring a browser-oriented HTTP client).
ARG PRIME_AGENT_RELEASE_BASE_URL=https://pub-728493de92a943e2a9b2d17b4719f318.r2.dev
ARG PRIME_AGENT_RELEASE_CHANNEL=stable
ARG PRIME_AGENT_VERSION=

RUN set -eux; \
    version="$PRIME_AGENT_VERSION"; \
    if [ -z "$version" ]; then \
        version="$(curl -fsSL "$PRIME_AGENT_RELEASE_BASE_URL/$PRIME_AGENT_RELEASE_CHANNEL")"; \
    fi; \
    version="${version#v}"; \
    echo "Installing prime-agent v$version"; \
    tmp="$(mktemp -d)"; \
    curl --retry 5 --retry-all-errors --retry-delay 2 -fsSL "$PRIME_AGENT_RELEASE_BASE_URL/releases/v$version/prime-agent-$version.tgz" -o "$tmp/prime-agent.tgz"; \
    curl --retry 5 --retry-all-errors --retry-delay 2 -fsSL "$PRIME_AGENT_RELEASE_BASE_URL/releases/v$version/prime-agent-core-$version.tgz" -o "$tmp/prime-agent-core.tgz"; \
    npm install -g --allow-remote=all --allow-file=all --allow-directory=all --allow-git=all "$tmp/prime-agent-core.tgz" "$tmp/prime-agent.tgz"; \
    rm -rf "$tmp"; \
    npm cache clean --force

USER agent
WORKDIR /home/agent

# Prepare the IPython kernel runtime (uv, Python, ipykernel) at build time
# so the first `prime-agent` invocation doesn't need to bootstrap it.
ENV PATH="/home/agent/.local/bin:/home/agent/bin:${PATH}"
RUN PRIME_AGENT_BOOTSTRAP_KERNEL_ON_INSTALL=1 PRIME_AGENT_INSTALL_UV=1 \
    node "$(npm root -g)/prime-agent/dist/postinstall.js" || true

WORKDIR /workspace

# ---------------------------------------------------------------------------
# System-wide proxychains-ng, driven by the HOST's real, already-configured
# /etc/proxychains.conf — not a config guessed/baked in at image build time.
#
# The image only sets LD_PRELOAD + PROXYCHAINS_CONF_FILE (matching the
# host's own env: LD_PRELOAD=/usr/lib/libproxychains4.so,
# PROXYCHAINS_CONF_FILE=/etc/proxychains.conf). At `docker run` time you
# bind-mount the host's actual /etc/proxychains.conf read-only over the
# container's copy, and run with --network host so any proxy entries in it
# that point at 127.0.0.1:<port> resolve to the very same local proxy
# process already running on the host. Every process in the container
# (prime-agent's own network calls, docker build/buildx, git, curl, etc.)
# then transparently goes through your existing proxychains setup, exactly
# as it does outside the container — no image rebuild needed if the host
# proxy config changes.
# ---------------------------------------------------------------------------
ENV LD_PRELOAD=/usr/lib/libproxychains4.so \
    PROXYCHAINS_CONF_FILE=/etc/proxychains4.conf \
    PROXYCHAINS_QUIET_MODE=1

# Persist agent config/sessions/auth across container runs by mounting a
# volume (or bind mount) at /home/agent/.prime.
VOLUME ["/home/agent/.prime"]

ENTRYPOINT ["prime-agent"]
#ENTRYPOINT ["bash"]
CMD []
