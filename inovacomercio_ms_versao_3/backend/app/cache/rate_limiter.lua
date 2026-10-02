-- Token Bucket distribuído.
-- KEYS[1] = chave do limite (ex.: ratelimit:user:email)
-- ARGV[1] = max_tokens, ARGV[2] = refill_rate (tokens/s), ARGV[3] = now (epoch), ARGV[4] = requested
-- Retorno: {allowed (0/1), tokens_restantes}

local chave = KEYS[1]
local max_tokens = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local agora = tonumber(ARGV[3])
local pedido = tonumber(ARGV[4])

local dados = redis.call('HMGET', chave, 'tokens', 'last_update')
local tokens = tonumber(dados[1])
local ultima_atualizacao = tonumber(dados[2])

if tokens == nil or ultima_atualizacao == nil then
    tokens = max_tokens
    ultima_atualizacao = agora
end

local decorrido = math.max(0, agora - ultima_atualizacao)
tokens = math.min(max_tokens, tokens + decorrido * refill_rate)

local permitido = 0
if tokens >= pedido then
    permitido = 1
    tokens = tokens - pedido
end

redis.call('HSET', chave, 'tokens', tokens, 'last_update', agora)

local ttl = math.ceil(max_tokens / math.max(refill_rate, 0.0001)) + 60
redis.call('EXPIRE', chave, ttl)

return {permitido, tokens}
