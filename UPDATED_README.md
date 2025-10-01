# Text Toner - Updated Chatbot Application

This is an updated version of the Text Toner chatbot application with improved tone detection and text improvement capabilities using FLAN-T5 XL model.

## 🚀 Key Updates

### Backend Changes
- **Replaced NLP module** with FLAN-T5 XL for better tone detection and text improvement
- **Simplified tone categories** to general tones: positive, negative, neutral
- **New single endpoint**: `POST /api/v1/tone/analyze-tone`
- **Enhanced error handling** and logging for model inference failures
- **Optimized for speed** and large text input (up to 2000 characters)

### Frontend Changes
- **Updated UI** to display original text, detected tone, and improved text
- **Added target tone selector** for users to specify desired tone
- **Enhanced message formatting** with visual tone indicators
- **Improved user experience** with better error handling

## 📋 API Endpoints

### POST /api/v1/tone/analyze-tone

**Input:**
```json
{
    "text": "Your text here",
    "target_tone": "optional_desired_tone"
}
```

**Output:**
```json
{
    "original_text": "Your text here",
    "detected_tone": "positive|negative|neutral",
    "improvised_text": "Improved version of your text"
}
```

**Supported Target Tones:**
- `positive` - Make text more upbeat and positive
- `negative` - Make text more critical or negative
- `neutral` - Make text more objective and neutral
- `professional` - Make text more formal and professional
- `friendly` - Make text more warm and friendly
- `formal` - Make text more structured and formal

## 🛠️ Installation & Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd text_toner_backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DATABASE=tone_analyzer_db
   HUGGINGFACE_MODEL=google/flan-t5-xl
   HUGGINGFACE_TOKEN=your_token_here
   API_HOST=0.0.0.0
   API_PORT=8000
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ```

4. **Run the backend:**
   ```bash
   python start.py
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd Text_toner_Frontend
   ```

2. **Install Flutter dependencies:**
   ```bash
   flutter pub get
   ```

3. **Run the Flutter app:**
   ```bash
   flutter run
   ```

   For web:
   ```bash
   flutter run -d web
   ```

## 🧪 Testing

### Backend API Testing

Run the test script to verify the API:

```bash
cd text_toner_backend
python test_api.py
```

This will test:
- Health check endpoint
- Supported tones endpoint
- Tone analysis with various test cases

### Manual Testing

1. **Start the backend server**
2. **Start the Flutter frontend**
3. **Test different scenarios:**
   - Type a message and see tone detection
   - Use the tone selector to specify target tone
   - Try different types of text (positive, negative, neutral)

## 📱 Features

### User Interface
- **Chat Interface**: Clean, modern chat UI with message bubbles
- **Tone Selector**: Toggle button to select target tone for text improvement
- **Quick Actions**: Pre-defined quick action chips for common improvements
- **Visual Feedback**: Color-coded tone indicators and improved text display

### Tone Analysis
- **Automatic Detection**: Detects general tone (positive, negative, neutral)
- **Text Improvement**: Generates improved version based on target tone
- **Preserves Meaning**: Maintains original meaning while adjusting tone
- **Multi-lingual Support**: Works with various languages (via FLAN-T5 XL)

## 🔧 Configuration

### Model Configuration
The application uses FLAN-T5 XL by default. You can switch to GPT-Neo 1.3B by updating the environment variable:

```env
HUGGINGFACE_MODEL=EleutherAI/gpt-neo-1.3B
```

### Text Length Limits
- Maximum input text length: 2000 characters
- Model processes up to 512 tokens per request
- Automatic truncation for longer texts

## 🚨 Troubleshooting

### Common Issues

1. **Model Loading Errors**
   - Ensure you have sufficient RAM (8GB+ recommended for FLAN-T5 XL)
   - Check internet connection for model download
   - Verify Hugging Face token if using private models

2. **API Connection Issues**
   - Verify backend is running on correct port (8000)
   - Check CORS settings in backend
   - Ensure frontend API URL is correct

3. **Performance Issues**
   - First request may be slow due to model loading
   - Consider using GPU for faster inference
   - Monitor memory usage during processing

### Logs
Check backend logs for detailed error information:
```bash
tail -f logs/app.log
```

## 📊 Performance

- **Model Size**: FLAN-T5 XL (~3GB)
- **Memory Usage**: ~6-8GB RAM recommended
- **Response Time**: 2-5 seconds per request (first request may take longer)
- **Concurrent Requests**: Limited by available memory

## 🔮 Future Enhancements

- [ ] Support for more languages
- [ ] Batch processing for multiple texts
- [ ] Custom tone training
- [ ] Voice input/output
- [ ] Mobile app optimization
- [ ] Caching for faster responses

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue on GitHub
4. Contact the development team

---

**Note**: This application requires a machine with sufficient RAM (8GB+) to run the FLAN-T5 XL model effectively. For production use, consider using a GPU-enabled server or cloud instance.
