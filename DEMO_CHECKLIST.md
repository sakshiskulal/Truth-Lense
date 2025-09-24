# TruthLens Hackathon Demo Checklist

## Pre-Demo Setup (15 minutes)

### 1. Environment Setup
- [ ] Copy `.env.sample` to `.env`
- [ ] Update JWT_SECRET with unique value
- [ ] Add Polygon Mumbai RPC URL
- [ ] Add test wallet private key
- [ ] Start all services: `docker-compose up -d`

### 2. Smart Contract Deployment
```bash
cd blockchain
npm install
npx hardhat run scripts/deploy.js --network mumbai
# Copy contract address to .env
```

### 3. Test Data Preparation
- [ ] Sample real image (JPG, < 6MB)
- [ ] Sample deepfake image (JPG, < 6MB)
- [ ] Sample video file (MP4, < 50MB)
- [ ] Sample audio file (MP3, < 20MB)

### 4. Azure Setup (Optional)
- [ ] Get Azure credentials from hackathon organizers
- [ ] Update `.env` with Azure keys
- [ ] Restart backend: `docker-compose restart backend`

## Demo Script (5 minutes)

### 1. Introduction (30 seconds)
**What to say:**
"TruthLens is a comprehensive media verification platform that uses AI detection, Azure Cognitive Services, news verification, and blockchain storage to verify the authenticity of uploaded media files."

**What to show:**
- Clean, modern homepage
- Feature highlights
- Professional UI design

### 2. User Registration (30 seconds)
**What to do:**
1. Click "Sign Up" button
2. Enter email: `demo@truthlens.com`
3. Enter password: `demo123`
4. Click "Create Account"

**What to say:**
"We have a secure JWT-based authentication system that protects user data and verification history."

### 3. File Upload & Analysis (2 minutes)
**What to do:**
1. Click "Upload" in navigation
2. Select sample image file
3. Add metadata: "Sample image for verification"
4. Click "Upload and Analyze"
5. Wait for analysis to complete

**What to say:**
"Our AI detection system analyzes the file using multiple techniques:
- Face consistency analysis
- Edge artifact detection
- Color space analysis
- Temporal consistency (for videos)"

**What to show:**
- Real-time upload progress
- Trust score calculation
- Detailed analysis breakdown
- Verdict (Real/Fake)

### 4. Azure Integration (1 minute)
**What to do:**
1. Show current analysis without Azure
2. Enable Azure services in `.env`
3. Restart backend
4. Upload same file again
5. Compare results

**What to say:**
"When Azure services are enabled, we get additional verification from Microsoft's Computer Vision API, providing enhanced accuracy and confidence scores."

**What to show:**
- Azure analysis results
- Improved trust score
- Additional verification data

### 5. Blockchain Verification (1 minute)
**What to do:**
1. Show result with "Real" verdict
2. Click "View on Blockchain" link
3. Open Polygonscan transaction
4. Explain blockchain benefits

**What to say:**
"For verified content, we store the file hash on Polygon Mumbai blockchain, providing immutable proof of verification. This creates a permanent record that can't be tampered with."

**What to show:**
- Transaction hash
- Polygonscan transaction details
- File hash stored on-chain
- Timestamp and uploader info

### 6. History & Results (30 seconds)
**What to do:**
1. Navigate to "History"
2. Show list of previous verifications
3. Click on a result to show details

**What to say:**
"Users can view their complete verification history and access detailed analysis results anytime."

## Demo Tips

### Technical Setup
- [ ] Test all flows before demo
- [ ] Have backup files ready
- [ ] Keep terminal open for troubleshooting
- [ ] Monitor logs: `docker-compose logs -f`

### Presentation Tips
- [ ] Speak clearly and confidently
- [ ] Explain technical concepts simply
- [ ] Show enthusiasm for the project
- [ ] Be prepared for questions
- [ ] Have a backup plan if something fails

### Common Questions & Answers

**Q: How accurate is the AI detection?**
A: Our current demo uses deterministic scoring, but in production we integrate with state-of-the-art models like Facebook's TimeSformer for video analysis and Microsoft's Computer Vision API for enhanced accuracy.

**Q: What happens if Azure is down?**
A: The system gracefully falls back to local AI detection and news verification, ensuring continuous operation.

**Q: Why use blockchain?**
A: Blockchain provides immutable proof of verification, creating a permanent record that can't be tampered with. This is crucial for legal and audit purposes.

**Q: How do you handle different file types?**
A: We support images (JPG, PNG), videos (MP4), and audio (MP3, WAV) with specialized detection models for each modality.

**Q: Is this production-ready?**
A: The core architecture is production-ready, but we're using demo models for the hackathon. Real ML models would be integrated for production deployment.

## Troubleshooting

### If Backend Fails
```bash
docker-compose restart backend
docker-compose logs backend
```

### If Frontend Fails
```bash
docker-compose restart frontend
docker-compose logs frontend
```

### If Database Fails
```bash
docker-compose restart mysql
docker-compose logs mysql
```

### If Blockchain Fails
- Check RPC URL and private key
- Ensure test wallet has MATIC tokens
- Verify contract address in `.env`

## Success Metrics

### What Judges Should See
- [ ] Professional, polished UI
- [ ] Smooth user experience
- [ ] Real-time analysis results
- [ ] Working blockchain integration
- [ ] Comprehensive verification system
- [ ] Scalable architecture

### Key Differentiators
- [ ] Multi-modal verification (image, video, audio)
- [ ] Azure Cognitive Services integration
- [ ] Blockchain immutability
- [ ] News verification
- [ ] Weighted trust scoring
- [ ] Modern tech stack
- [ ] Production-ready architecture