docker run -it --rm \
     --network host \
     -v /etc/proxychains4.conf:/etc/proxychains4.conf:ro \
     -v /var/run/docker.sock:/var/run/docker.sock \
     --group-add "$(stat -c '%g' /var/run/docker.sock)" \
     -e OPENROUTER_API_KEY="sk-or-v1-......." \
     -v "$PWD/${1}":/workspace \
     -v "$PWD/.skills":/workspace/.skills \
     -v prime-agent-config:/home/agent/.prime \
     -w /workspace \
     prime-agent

### Aso you can use
#     -e OPENAI_API_KEY="..." \
#     -e OPENROUTER_API_KEY="..." \
