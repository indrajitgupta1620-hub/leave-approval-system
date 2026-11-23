const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;

let leaves = [
    {
        id: "1",
        user: "Alfiya",
        reason: "Annual Vacation",
        start: "2026-12-01",
        end: "2026-12-05",
        status: "Pending"
    }
];

function setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

function sendJson(res, statusCode, data) {
    setCorsHeaders(res);
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data, null, 2));
}

function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => { body += chunk; });
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (err) {
                reject(err);
            }
        });
        req.on('error', err => reject(err));
    });
}

async function requestHandler(req, res) {
    setCorsHeaders(res);

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;

    try {
        if (!pathname.startsWith('/api') && req.method === 'GET') {
            const htmlPath = path.join(__dirname, 'index.html');
            if (fs.existsSync(htmlPath)) {
                res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
                return res.end(fs.readFileSync(htmlPath));
            }
        }

        if (pathname === '/api/health' && req.method === 'GET') {
            return sendJson(res, 200, {
                status: 'UP',
                message: 'Leave Approval API is running smoothly',
                timestamp: new Date().toISOString()
            });
        }

        if (pathname === '/api/login' && req.method === 'POST') {
            const body = await parseBody(req);
            if (!body.username || !body.role) {
                return sendJson(res, 400, { error: 'Username and role are required' });
            }
            return sendJson(res, 200, {
                message: 'Login successful',
                user: {
                    username: body.username,
                    role: body.role
                }
            });
        }

        if (pathname === '/api/leaves' && req.method === 'GET') {
            const filterUser = parsedUrl.query.user;
            if (filterUser) {
                const userLeaves = leaves.filter(l => l.user.toLowerCase() === filterUser.toLowerCase());
                return sendJson(res, 200, { total: userLeaves.length, leaves: userLeaves });
            }
            return sendJson(res, 200, { total: leaves.length, leaves });
        }

        if (pathname === '/api/leaves' && req.method === 'POST') {
            const body = await parseBody(req);
            const { user, reason, start, end } = body;

            if (!user || !reason || !start || !end) {
                return sendJson(res, 400, { error: 'Missing required fields: user, reason, start, end' });
            }

            if (new Date(end) < new Date(start)) {
                return sendJson(res, 400, { error: 'End date cannot be earlier than start date' });
            }

            const newLeave = {
                id: (leaves.length + 1).toString(),
                user,
                reason,
                start,
                end,
                status: 'Pending'
            };

            leaves.push(newLeave);
            return sendJson(res, 201, {
                message: 'Leave applied successfully',
                leave: newLeave
            });
        }

        if (pathname.startsWith('/api/leaves/') && (req.method === 'PUT' || req.method === 'PATCH')) {
            const id = pathname.split('/')[3];
            const body = await parseBody(req);
            const { status } = body;

            if (!['Approved', 'Rejected'].includes(status)) {
                return sendJson(res, 400, { error: 'Status must be Approved or Rejected' });
            }

            const leave = leaves.find(l => l.id === id);
            if (!leave) {
                return sendJson(res, 404, { error: `Leave with ID ${id} not found` });
            }

            leave.status = status;
            return sendJson(res, 200, {
                message: `Leave ${status.toLowerCase()} successfully`,
                leave
            });
        }

        if (pathname.startsWith('/api/leaves/') && req.method === 'DELETE') {
            const id = pathname.split('/')[3];
            const index = leaves.findIndex(l => l.id === id);
            if (index === -1) {
                return sendJson(res, 404, { error: `Leave with ID ${id} not found` });
            }

            const deleted = leaves.splice(index, 1)[0];
            return sendJson(res, 200, {
                message: 'Leave deleted successfully',
                leave: deleted
            });
        }

        return sendJson(res, 404, { error: 'Endpoint not found' });
    } catch (err) {
        return sendJson(res, 500, { error: 'Internal Server Error', details: err.message });
    }
}

const server = http.createServer(requestHandler);

if (require.main === module) {
    server.listen(PORT, () => {
        console.log(`Leave Approval API Server is running at http://localhost:${PORT}`);
        console.log(`Health check: http://localhost:${PORT}/api/health`);
        console.log(`Leaves list:  http://localhost:${PORT}/api/leaves`);
    });
}

module.exports = requestHandler;
