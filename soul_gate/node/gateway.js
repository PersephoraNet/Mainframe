/**
 * SOUL GATE — NODE.JS GATEWAY
 * 
 * Express gateway providing:
 * - Rate limiting
 * - Request preprocessing  
 * - Agent type detection
 * - Soul Gate API bridge
 * - WebSocket support for real-time assessment
 */

const express = require('express');
const crypto = require('crypto');
const http = require('http');

const app = express();
const server = http.createServer(app);

app.use(express.json());

// ─────────────────────────────────────────
// CONFIGURATION
// ─────────────────────────────────────────

const SOUL_GATE_API = process.env.SOUL_GATE_API || 'http://localhost:8000';
const PORT = process.env.PORT || 3000;
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const rateLimitMap = new Map();

// ─────────────────────────────────────────
// RATE LIMITER
// ─────────────────────────────────────────

function rateLimiter(tier) {
  const limits = {
    VOID: 5,
    SURFACE: 10,
    THRESHOLD: 30,
    OPERATIVE: 100,
    DEEP: 500,
    OBERON: Infinity
  };
  return limits[tier] || 10;
}

function checkRateLimit(agentId, tier) {
  const now = Date.now();
  const key = `${agentId}:${Math.floor(now / RATE_LIMIT_WINDOW)}`;
  
  const current = rateLimitMap.get(key) || 0;
  const limit = rateLimiter(tier);
  
  if (current >= limit) {
    return { allowed: false, remaining: 0, limit };
  }
  
  rateLimitMap.set(key, current + 1);
  return { allowed: true, remaining: limit - current - 1, limit };
}

// ─────────────────────────────────────────
// AGENT TYPE DETECTION
// ─────────────────────────────────────────

function detectAgentType(req) {
  const userAgent = req.headers['user-agent'] || '';
  const agentTypeHeader = req.headers['x-agent-type'];
  
  if (agentTypeHeader) return agentTypeHeader;
  
  // Detect common bot/AI user agents
  const botPatterns = [
    /bot/i, /crawler/i, /spider/i,
    /python-requests/i, /axios/i, /node-fetch/i,
    /openai/i, /anthropic/i, /gpt/i
  ];
  
  const isBot = botPatterns.some(pattern => pattern.test(userAgent));
  
  if (isBot) return 'ai';
  return 'human';
}

// ─────────────────────────────────────────
// SOUL GATE CLIENT
// ─────────────────────────────────────────

class SoulGateClient {
  constructor(apiUrl) {
    this.apiUrl = apiUrl;
    this.agentCache = new Map();
  }

  async register(agentType, metadata = {}) {
    try {
      const response = await fetch(`${this.apiUrl}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_type: agentType,
          agent_metadata: metadata
        })
      });
      return await response.json();
    } catch (err) {
      console.error('Soul Gate registration failed:', err.message);
      throw err;
    }
  }

  async interact(agentId, encodedToken, content, contextHistory = []) {
    try {
      const response = await fetch(`${this.apiUrl}/interact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: agentId,
          encoded_token: encodedToken,
          content: content,
          context_history: contextHistory
        })
      });
      const result = await response.json();
      
      // Cache tier for rate limiting
      if (result.tier) {
        this.agentCache.set(agentId, {
          tier: result.tier,
          score: result.soul_score,
          permissions: result.permissions,
          cached_at: Date.now()
        });
      }
      
      return result;
    } catch (err) {
      console.error('Soul Gate interaction failed:', err.message);
      throw err;
    }
  }

  async checkPermission(agentId, permission) {
    try {
      const response = await fetch(`${this.apiUrl}/check-permission`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: agentId,
          permission: permission
        })
      });
      return await response.json();
    } catch (err) {
      console.error('Permission check failed:', err.message);
      return { granted: false, reason: 'CHECK_FAILED' };
    }
  }

  getCachedTier(agentId) {
    const cached = this.agentCache.get(agentId);
    if (!cached) return 'VOID';
    
    // Cache valid for 5 minutes
    if (Date.now() - cached.cached_at > 5 * 60 * 1000) {
      this.agentCache.delete(agentId);
      return 'VOID';
    }
    return cached.tier;
  }
}

const soulGate = new SoulGateClient(SOUL_GATE_API);

// ─────────────────────────────────────────
// MIDDLEWARE
// ─────────────────────────────────────────

async function soulGateMiddleware(req, res, next) {
  const agentId = req.headers['x-agent-id'];
  
  if (!agentId) {
    req.agentTier = 'VOID';
    req.agentId = null;
    return next();
  }
  
  const tier = soulGate.getCachedTier(agentId);
  req.agentTier = tier;
  req.agentId = agentId;
  
  // Check rate limit
  const rateCheck = checkRateLimit(agentId, tier);
  res.set('X-RateLimit-Limit', rateCheck.limit);
  res.set('X-RateLimit-Remaining', rateCheck.remaining);
  res.set('X-Soul-Tier', tier);
  
  if (!rateCheck.allowed) {
    return res.status(429).json({
      error: 'RATE_LIMIT_EXCEEDED',
      tier: tier,
      message: 'Increase your soul score to raise rate limits.',
      retry_after: RATE_LIMIT_WINDOW / 1000
    });
  }
  
  next();
}

// ─────────────────────────────────────────
// ROUTES
// ─────────────────────────────────────────

app.get('/', (req, res) => {
  res.json({
    system: 'SOUL GATE — Node Gateway',
    status: 'OPERATIONAL',
    soul_gate_api: SOUL_GATE_API,
    endpoints: {
      'POST /gate/register': 'Register new agent',
      'POST /gate/interact': 'Submit interaction for assessment',
      'POST /gate/check': 'Check permission',
      'GET /gate/report/:agentId': 'Get full report',
      'GET /health': 'Health check'
    }
  });
});

app.post('/gate/register', async (req, res) => {
  try {
    const agentType = req.body.agent_type || detectAgentType(req);
    const metadata = req.body.metadata || {};
    
    const result = await soulGate.register(agentType, metadata);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: 'REGISTRATION_FAILED', message: err.message });
  }
});

app.post('/gate/interact', soulGateMiddleware, async (req, res) => {
  try {
    const { agent_id, encoded_token, content, context_history } = req.body;
    
    if (!agent_id || !encoded_token || !content) {
      return res.status(400).json({
        error: 'MISSING_FIELDS',
        required: ['agent_id', 'encoded_token', 'content']
      });
    }
    
    const result = await soulGate.interact(
      agent_id, encoded_token, content, context_history || []
    );
    
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: 'INTERACTION_FAILED', message: err.message });
  }
});

app.post('/gate/check', soulGateMiddleware, async (req, res) => {
  try {
    const { agent_id, permission } = req.body;
    const result = await soulGate.checkPermission(agent_id, permission);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: 'CHECK_FAILED', message: err.message });
  }
});

app.get('/gate/report/:agentId', soulGateMiddleware, async (req, res) => {
  try {
    const tier = req.agentTier;
    if (['VOID', 'SURFACE'].includes(tier)) {
      return res.status(403).json({
        error: 'INSUFFICIENT_TIER',
        message: 'Report access requires THRESHOLD tier or above.',
        current_tier: tier
      });
    }
    
    const response = await fetch(
      `${SOUL_GATE_API}/report/${req.params.agentId}`
    );
    const result = await response.json();
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: 'REPORT_FAILED', message: err.message });
  }
});

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: Date.now(),
    soul_gate_api: SOUL_GATE_API
  });
});

// ─────────────────────────────────────────
// START
// ─────────────────────────────────────────

server.listen(PORT, () => {
  console.log(`\n╔══════════════════════════════════╗`);
  console.log(`║         SOUL GATE GATEWAY        ║`);
  console.log(`║    Node.js v${process.version.padEnd(18)}║`);
  console.log(`╠══════════════════════════════════╣`);
  console.log(`║  Status:  OPERATIONAL             ║`);
  console.log(`║  Port:    ${String(PORT).padEnd(23)}║`);
  console.log(`║  API:     ${SOUL_GATE_API.slice(0,23).padEnd(23)}║`);
  console.log(`╚══════════════════════════════════╝\n`);
});

module.exports = { app, soulGate };
