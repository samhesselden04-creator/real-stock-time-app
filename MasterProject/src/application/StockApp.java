package application;
import javax.swing.*;

import javax.swing.text.*;
import java.awt.*;
import java.net.URI;

import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;

import java.util.concurrent.Executors;
import java.time.Duration;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import java.lang.management.ManagementFactory;
import com.sun.management.OperatingSystemMXBean;
public class StockApp extends JFrame {

    private Timer mainTimer;
    private Timer tslaTimer;
    private Timer aaplTimer;
    private Timer amznTimer;
    private StockGraphPanel mainGraphPanel;
    private StockGraphPanel tslaGraphPanel;
    private StockGraphPanel aaplGraphPanel;
    private StockGraphPanel amznGraphPanel;
    private CardLayout contentLayout;
    private JPanel contentPanel;
    private JTextArea performanceResults;


    private final HttpClient httpClient = HttpClient.newBuilder() .connectTimeout(Duration.ofSeconds(5)) .build();
    private final ExecutorService requestExecutor = Executors.newSingleThreadExecutor();
    private final Map<String, CompletableFuture<Double>> activeRequests = new ConcurrentHashMap<>();
    private final Object requestLock = new Object();

    private long lastApiRequestTime = 0;

    private static final long requestGap = 1150;
    private static final Pattern pricePattern = Pattern.compile("\"c\"\\s*:\\s*([0-9]+(?:\\.[0-9]+)?)");


    private static final String apiKey = "d96i16hr01qr77dkif1gd96i16hr01qr77dkif20";
    public StockApp() {

        setupWindow();
        createInterface();
        startStockUpdates();
        setupPerformanceTestShortcut();
    }
    //sets up window
    private void setupWindow() {
        setTitle("Java Stock Dashboard");
        setSize(1200, 700);

        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        getContentPane().setBackground(new Color(245, 247, 250));
    }
    //starts stock updates
    private void startStockUpdates() {
        startSideStockUpdates();
        startMainStockUpdates("TSLA");
    }
    //creates interface
    private void createInterface() {
        setLayout(new BorderLayout());
        JPanel sidebar = createSidebar();
        add(sidebar, BorderLayout.WEST);
        JPanel dashboard = new JPanel( new BorderLayout(20, 20) );
        dashboard.setBackground( new Color(245, 247, 250) );
        dashboard.setBorder( BorderFactory.createEmptyBorder( 20, 25, 20, 25 ) );

        JPanel header = createHeader();
        dashboard.add( header, BorderLayout.NORTH );
        JPanel centrePanel = new JPanel( new BorderLayout(15, 15) );
        centrePanel.setBackground( new Color(245, 247, 250) );
        JPanel searchPanel = createSearchArea();
        centrePanel.add( searchPanel, BorderLayout.NORTH );
        JPanel graphArea = createGraphs();
        centrePanel.add( graphArea, BorderLayout.CENTER );
        dashboard.add( centrePanel, BorderLayout.CENTER );
        JPanel performancePanel = createPerformancePanel();
        contentLayout = new CardLayout();

        contentPanel = new JPanel(contentLayout);
        contentPanel.setBackground(new Color(245, 247, 250));
        contentPanel.add(dashboard, "dashboard");
        contentPanel.add(performancePanel, "performance");
        add( contentPanel, BorderLayout.CENTER );

    }

    //creates sidebar
    private JPanel createSidebar() {
        JPanel sidebar = new JPanel();
        sidebar.setPreferredSize( new Dimension(180, 700) );

        sidebar.setBackground( new Color(31, 41, 55) );
        sidebar.setLayout( new BoxLayout( sidebar, BoxLayout.Y_AXIS ) );
        sidebar.setBorder( BorderFactory.createEmptyBorder( 25, 15, 25, 15 ) );
        JLabel title = new JLabel( "Stock Dashboard" );
        title.setForeground(Color.WHITE);
        title.setFont( new Font( "SansSerif", Font.BOLD, 20 ) );
        title.setAlignmentX( Component.LEFT_ALIGNMENT );
        sidebar.add(title);

        sidebar.add( Box.createVerticalStrut(40) );

        JButton dashboardButton = new JButton("▦  Dashboard");
        dashboardButton.setAlignmentX( Component.LEFT_ALIGNMENT );
        dashboardButton.setMaximumSize( new Dimension( Integer.MAX_VALUE, 45 ) );

        dashboardButton.setForeground(Color.WHITE);
        dashboardButton.setBackground( new Color(55, 75, 100) );

        dashboardButton.setFocusPainted(false);
        dashboardButton.setBorderPainted(false);
        sidebar.add(dashboardButton);
        JButton performanceButton = new JButton("▥  Performance");

        performanceButton.setAlignmentX( Component.LEFT_ALIGNMENT );
        performanceButton.setMaximumSize( new Dimension( Integer.MAX_VALUE, 45 ) );
        performanceButton.setForeground(Color.WHITE);
        performanceButton.setBackground( new Color(55, 75, 100) );
        performanceButton.setFocusPainted(false);


        performanceButton.setBorderPainted(false);
        performanceButton.addActionListener(e -> { contentLayout.show(contentPanel, "performance"); });
        dashboardButton.addActionListener(e -> { contentLayout.show(contentPanel, "dashboard"); });
        sidebar.add(Box.createVerticalStrut(10));
        sidebar.add(performanceButton);
        return sidebar;

    }
    //creates performance panel
    private JPanel createPerformancePanel() {
        JPanel panel = new JPanel(new BorderLayout(20, 20));
        panel.setBackground(new Color(245, 247, 250));
        panel.setBorder( BorderFactory.createEmptyBorder(20, 25, 20, 25) );
        JLabel title = new JLabel("Performance Testing");
        title.setFont(new Font("SansSerif", Font.BOLD, 26));
        title.setForeground(new Color(31, 41, 55));
        JLabel description = new JLabel("Measure API response time, memory usage and CPU utilisation of the application.");
        description.setForeground(new Color(90, 100, 110));
        JPanel header = new JPanel();
        header.setLayout(new BoxLayout(header, BoxLayout.Y_AXIS));
        header.setBackground(new Color(245, 247, 250));
        header.add(title);

        header.add(Box.createVerticalStrut(6));

        header.add(description);
        panel.add(header, BorderLayout.NORTH);


        JPanel centre = new JPanel(new BorderLayout(15, 15));
        centre.setBackground(new Color(245, 247, 250));
        JButton runButton = new JButton("Run Performance Test");
        runButton.setFocusPainted(false);
        runButton.setFont(new Font("SansSerif", Font.BOLD, 14));
        runButton.addActionListener(e -> runPerformanceTest());


        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 0, 0));
        buttonPanel.setBackground(new Color(245, 247, 250));
        buttonPanel.add(runButton);

        performanceResults = new JTextArea();
        performanceResults.setEditable(false);
        performanceResults.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 14));
        performanceResults.setBackground(Color.WHITE);
        performanceResults.setBorder( BorderFactory.createCompoundBorder( BorderFactory.createLineBorder(new Color(220,
                225, 230)), BorderFactory.createEmptyBorder(15, 15, 15, 15) ) );
        performanceResults.setText( "No performance test has been run yet.\n\n" +
                    "Click 'Run Performance Test' to measure the current Java application." );

        centre.add(buttonPanel, BorderLayout.NORTH);
        centre.add(new JScrollPane(performanceResults), BorderLayout.CENTER);

        panel.add(centre, BorderLayout.CENTER);
        return panel;

    }
    //creates header
    private JPanel createHeader() {
        JPanel header = new JPanel( new BorderLayout() );
        header.setBackground( new Color(245, 247, 250) );
        JLabel title = new JLabel( "Market Dashboard" );
        title.setFont( new Font( "SansSerif", Font.BOLD, 28 ) );
        title.setForeground( new Color(30, 41, 59) );
        JLabel connection = new JLabel( "● Live connection" );

        connection.setFont( new Font( "SansSerif", Font.PLAIN, 14 ) );
        connection.setForeground( new Color(30, 160, 100) );


        header.add( title, BorderLayout.WEST );
        header.add( connection, BorderLayout.EAST );
        return header;
    }

    //creates search area
    private JPanel createSearchArea() {
        JPanel searchCard = new JPanel( new BorderLayout(10, 10) );
        searchCard.setBackground(Color.WHITE);
        searchCard.setBorder( BorderFactory.createCompoundBorder( BorderFactory.createLineBorder( new Color(225,
                    230, 235) ), BorderFactory.createEmptyBorder( 15, 18, 15, 18 ) ) );
        JLabel searchTitle = new JLabel( "Search for a stock" );
        searchTitle.setFont( new Font( "SansSerif", Font.BOLD, 15 ) );
        searchTitle.setForeground( new Color(30, 41, 59) );

        JPanel searchControls = new JPanel( new BorderLayout(10, 0) );
        searchControls.setBackground(Color.WHITE);
        JTextField searchBar = new JTextField();
        searchBar.setToolTipText( "Enter a ticker such as TSLA" );
        searchBar.setPreferredSize( new Dimension(250, 38) );
        ((AbstractDocument) searchBar.getDocument()) .setDocumentFilter( new StockCodeFilter() );
        JButton searchButton = new JButton("Search");
        searchButton.setPreferredSize( new Dimension(100, 38) );
        searchButton.setBackground( new Color(40, 110, 220) );
        searchButton.setForeground(Color.WHITE);
        searchButton.setFocusPainted(false);
        searchControls.add( searchBar, BorderLayout.CENTER );


        searchControls.add( searchButton, BorderLayout.EAST );
        JPanel content = new JPanel( new BorderLayout(0, 8) );
        content.setBackground(Color.WHITE);


        content.add( searchTitle, BorderLayout.NORTH );
        content.add( searchControls, BorderLayout.CENTER );
        searchCard.add( content, BorderLayout.CENTER );
        searchButton.addActionListener(e -> {
            String stockCode = searchBar.getText() .trim() .toUpperCase();
            if (!stockCode.matches( "[A-Za-z0-9]{1,5}" )) {

                JOptionPane.showMessageDialog( this, "Stock code must contain 1-5 letters/numbers.",
                    "Invalid Input", JOptionPane.ERROR_MESSAGE );
                return; }
            checkStockExistsThenStart( stockCode ); });
        searchBar.addActionListener(e -> searchButton.doClick() );

        return searchCard;
    }
    //creates stock graphs
    private JPanel createGraphs() {
        JPanel graphArea = new JPanel( new BorderLayout(15, 15) );
        graphArea.setBackground( new Color(245, 247, 250) );
        mainGraphPanel = new StockGraphPanel("TSLA");
        mainGraphPanel.setBorder( BorderFactory.createTitledBorder( "Main Stock Graph" ) );
        tslaGraphPanel = new StockGraphPanel("TSLA");
        aaplGraphPanel = new StockGraphPanel("AAPL");
        amznGraphPanel = new StockGraphPanel("AMZN");

        tslaGraphPanel.setBorder( BorderFactory.createTitledBorder( "TSLA" ) );
        aaplGraphPanel.setBorder( BorderFactory.createTitledBorder( "AAPL" ) );

        amznGraphPanel.setBorder( BorderFactory.createTitledBorder( "AMZN" ) );

        JPanel mainPanel  =   new JPanel( new BorderLayout() );
        mainPanel.setBackground(Color.WHITE);
        mainPanel.add( mainGraphPanel, BorderLayout.CENTER );

        JPanel rightPanel = new JPanel( new GridLayout( 3, 1, 10, 10 ) );
        rightPanel.setBackground( new Color(245, 247, 250) );

        rightPanel.setPreferredSize( new Dimension(280, 0) );

        rightPanel.add(tslaGraphPanel);
        rightPanel.add(aaplGraphPanel);

        rightPanel.add(amznGraphPanel);
        graphArea.add( mainPanel, BorderLayout.CENTER );
        graphArea.add( rightPanel, BorderLayout.EAST );

        return graphArea;
    }
    //checks stock code
    private void checkStockExistsThenStart( String symbol ) {
        mainGraphPanel.setSymbol(symbol);
        mainGraphPanel.clearPrices();
        mainGraphPanel.setErrorMessage( "Checking stock code..." );
        fetchStockPriceOnce( symbol, price -> {
                    if (price <= 0) {
                        SwingUtilities.invokeLater(() -> mainGraphPanel.setErrorMessage( "Stock code not found" ) );
                    } else {
                        SwingUtilities.invokeLater(() -> startMainStockUpdates( symbol ) ); } } );
    }
    //starts main graph updates
    private void startMainStockUpdates( String symbol ) {
        if (mainTimer != null) {

            mainTimer.stop();
        }
        mainGraphPanel.setSymbol(symbol);
        mainGraphPanel.clearPrices();

        fetchStockPrice( symbol, mainGraphPanel );
        mainTimer = new Timer( 1000, e -> fetchStockPrice( symbol, mainGraphPanel ) );
        mainTimer.start();
    }
    //starts side graph updates
    private void startSideStockUpdates() {
        fetchStockPrice( "TSLA", tslaGraphPanel );
        fetchStockPrice( "AAPL", aaplGraphPanel );
        fetchStockPrice( "AMZN", amznGraphPanel );
        tslaTimer = new Timer( 15000, e -> fetchStockPrice( "TSLA", tslaGraphPanel ) );
        aaplTimer = new Timer( 15000, e -> fetchStockPrice( "AAPL", aaplGraphPanel ) );
        amznTimer = new Timer( 15000, e -> fetchStockPrice( "AMZN", amznGraphPanel ) );

        tslaTimer.start();
        aaplTimer.start();
        amznTimer.start();
    }

    //gets stock price
    private void fetchStockPrice( String symbol, StockGraphPanel graphPanel ) {

        fetchStockPriceOnce( symbol, price -> {
                    SwingUtilities.invokeLater(() -> {
                        if (price <= 0) {

                            graphPanel.setErrorMessage( "Unable to retrieve stock data" );


                        } else {
                            graphPanel.addPrice( price ); } }); } );
    }
    //gets stock price once
    private void fetchStockPriceOnce( String symbol, PriceCallback callback ) {
        String cleanSymbol = symbol.trim().toUpperCase();
        CompletableFuture<Double> request = activeRequests.computeIfAbsent( cleanSymbol,
            currentSymbol -> CompletableFuture.supplyAsync( () -> requestPrice(currentSymbol), requestExecutor ) );
        request.whenComplete((price, exception) -> {
            activeRequests.remove( cleanSymbol, request );
            if (exception != null || price == null) { callback.onPriceReceived(0); } else { callback.onPriceReceived(price); } });
    }

    //requests stock price
    private double requestPrice( String symbol ) {
        try {

            waitForApiSlot();
            HttpResponse<String> response = sendQuoteRequest(symbol);
            if (response.statusCode() == 429) {
                long retryDelay = getRetryDelay(response);
                Thread.sleep(retryDelay);
                waitForApiSlot();

                response = sendQuoteRequest(symbol);
            }
            if (response.statusCode() != 200) {
                return 0;
            }
            Matcher matcher = pricePattern.matcher( response.body() );
            if (!matcher.find()) {
                return 0;
            }

            return Double.parseDouble( matcher.group(1) );
        } catch (Exception exception) {
            return 0;
        }
    }
    //sends api request
    private HttpResponse<String> sendQuoteRequest( String symbol ) throws Exception {
        String url = "https://finnhub.io/api/v1/quote?symbol=" + symbol + "&token=" + apiKey;
        HttpRequest request = HttpRequest.newBuilder() .uri(URI.create(url)) .timeout(Duration.ofSeconds(8)) .GET() .build();
        return httpClient.send( request, HttpResponse.BodyHandlers.ofString() );


    }
    //waits for api
    private void waitForApiSlot() throws InterruptedException {
        synchronized (requestLock) {

            long currentTime = System.currentTimeMillis();
            long elapsed = currentTime - lastApiRequestTime;
            if (elapsed < requestGap) {
                Thread.sleep( requestGap - elapsed );
            }
            lastApiRequestTime = System.currentTimeMillis();
        }
    }

    //gets retry delay
    private long getRetryDelay( HttpResponse<String> response ) {
        String retryAfter = response.headers() .firstValue("Retry-After") .orElse("");

        try {
            return Math.max( 1000, Long.parseLong(retryAfter) * 1000 );
        } catch (NumberFormatException exception) {
            return 5000;
        }
    }
    private interface PriceCallback {
        //handles stock price
        void onPriceReceived( double price );
    }
    private static class StockGraphPanel extends JPanel {
        private final ArrayList<Double> prices = new ArrayList<>();
        private String symbol;
        private String errorMessage = "";
        public StockGraphPanel( String symbol ) {
            this.symbol = symbol;
            setBackground(Color.WHITE);
        }
        //changes stock symbol
        public void setSymbol( String symbol ) {
            this.symbol = symbol;

            errorMessage = "";

            repaint();
        }
        //adds stock price
        public void addPrice( double price ) {

            prices.add(price);

            if (prices.size() > 60) {
                prices.remove(0);
            }
            errorMessage = "";
            repaint();
        }
        //clears prices
        public void clearPrices() {
            prices.clear();

            repaint();
        }
        //shows error message
        public void setErrorMessage( String message ) {
            errorMessage = message;
            repaint();
        }
        //draws stock graph
        @Override protected void paintComponent( Graphics graphics ) {
            super.paintComponent( graphics );
            Graphics2D graphics2D = (Graphics2D) graphics.create();
            graphics2D.setRenderingHint( RenderingHints .KEY_ANTIALIASING, RenderingHints .VALUE_ANTIALIAS_ON );
            graphics2D.setStroke( new BasicStroke(2) );
            int width = getWidth();
            int height = getHeight();


            int padding = 45;
            graphics2D.setColor(Color.BLACK);
            graphics2D.drawString( symbol, padding, 25 );
            if (!errorMessage.isEmpty()) {
                graphics2D.drawString( errorMessage, padding, height / 2 );
                graphics2D.dispose();

                return;
            }
            if (prices.isEmpty()) {
                graphics2D.drawString( "Waiting for stock data...", padding, height / 2 );
                graphics2D.dispose();

                return;
            }
            if (prices.size() == 1) {

                double latestPrice = prices.get(0);

                int pointX = width / 2;
                int pointY = height / 2;


                graphics2D.setColor( new Color( 40, 110, 220 ) );
                graphics2D.fillOval( pointX - 5, pointY - 5, 10, 10 );

                graphics2D.setColor( Color.BLACK );

                graphics2D.drawString( "Latest Price: $" + String.format( "%.2f",
                        latestPrice ), padding, height - 15 );
                graphics2D.drawString( "Collecting more price data...", padding, height / 2 + 30 );
                graphics2D.dispose();

                return;
            }
            double minPrice = prices.stream() .min(Double::compare) .orElse(0.0);
            double maxPrice = prices.stream() .max(Double::compare) .orElse(1.0);
            if (maxPrice == minPrice) {
                maxPrice = minPrice + 1;
            }
            graphics2D.setColor( new Color( 220, 225, 230 ) );

            int horizontalLines = 5;
            for ( int line = 0; line <= horizontalLines; line++ ) {
                int yPosition = padding + ( line * ( height - 2 * padding ) / horizontalLines );
                graphics2D.drawLine( padding, yPosition, width - padding, yPosition );
            }
            graphics2D.setColor( Color.DARK_GRAY );
            graphics2D.drawLine( padding, height - padding, width - padding, height - padding );
            graphics2D.drawLine( padding, padding, padding, height - padding );
            int graphWidth = width - 2 * padding;
            int graphHeight = height - 2 * padding;
            if ( prices.get( prices.size() - 1 ) >= prices.get(0) ) {
                graphics2D.setColor( new Color( 30, 160, 100 ) );

            } else {
                graphics2D.setColor( new Color( 210, 60, 70 ) );

            }
            for ( int index = 0; index < prices.size() - 1; index++ ) {

                int x1 = padding + ( index * graphWidth / ( prices.size() - 1 ) );
                int x2 = padding + ( ( index + 1 ) * graphWidth / ( prices.size() - 1 ) );
                int y1 = height - padding - (int) ( ( prices.get(index) - minPrice ) / ( maxPrice - minPrice ) * graphHeight );
                int y2 = height - padding - (int) ( ( prices.get( index +
                            1 ) - minPrice ) / ( maxPrice - minPrice ) * graphHeight );
                graphics2D.drawLine( x1, y1, x2, y2 );

            }
            double latestPrice = prices.get( prices.size() - 1 );
            graphics2D.setColor( Color.BLACK );
            graphics2D.drawString( "Latest Price: $" + String.format( "%.2f",
                latestPrice ), padding, height - 15 );

            graphics2D.drawString( "Low: $" + String.format( "%.2f", minPrice ), padding, 42 );

            graphics2D.drawString( "High: $" + String.format( "%.2f", maxPrice ), width - padding - 90, 42 );
            graphics2D.dispose();
        }
    }

    private static class StockCodeFilter extends DocumentFilter {
        //checks typed text
        @Override public void insertString( FilterBypass filterBypass,
            int offset, String string, AttributeSet attributeSet ) throws BadLocationException {

            if (string == null) {
                return;
            }
            String currentText = filterBypass .getDocument() .getText( 0,
                        filterBypass .getDocument() .getLength() );
            String newText = currentText.substring( 0, offset ) + string + currentText.substring( offset );
            if (isValid(newText)) {
                super.insertString( filterBypass, offset, string.toUpperCase(), attributeSet );
            }
        }
        //checks replacement text
        @Override public void replace( FilterBypass filterBypass,
            int offset, int length, String text, AttributeSet attributeSet ) throws BadLocationException {
            String currentText = filterBypass .getDocument() .getText( 0,
                        filterBypass .getDocument() .getLength() );
            String replacementText = text == null ? "" : text;
            String newText = currentText.substring( 0, offset ) +
                        replacementText + currentText.substring( offset + length );
            if (isValid(newText)) {
                super.replace( filterBypass, offset, length, replacementText.toUpperCase(), attributeSet );

            }
        }
        //checks stock code
        private boolean isValid( String text ) {

            return text.length() <= 5 && text.matches( "[A-Za-z0-9]*" );
        }
    }
    //sets up test shortcut
    private void setupPerformanceTestShortcut() {
        getRootPane().getInputMap( JComponent.WHEN_IN_FOCUSED_WINDOW ).put( KeyStroke.getKeyStroke("control P"),
                    "runPerformanceTest" );


        getRootPane().getActionMap().put( "runPerformanceTest", new AbstractAction() {
                    //runs actionPerformed
                    @Override public void actionPerformed( java.awt.event.ActionEvent event ) { runPerformanceTest(); } } );
    }
    //runs performance test
    private void runPerformanceTest() {
        final int numberOfRequests = 10;
        new SwingWorker<PerformanceResult, Void>() {

            //runs test in background
            @Override protected PerformanceResult doInBackground() {
                OperatingSystemMXBean osBean = (OperatingSystemMXBean) ManagementFactory .getOperatingSystemMXBean();
                Runtime runtime = Runtime.getRuntime();
                long testStart = System.nanoTime();
                long cpuStart = osBean.getProcessCpuTime();
                long memoryTotal = 0;
                long memoryPeak = 0;
                long successfulRequests = 0;


                long fastest = Long.MAX_VALUE;
                long slowest = 0;
                long requestTimeTotal = 0;
                for (int requestNumber = 0; requestNumber < numberOfRequests; requestNumber++) {
                    long requestStart = 0;

                    try {
                        waitForApiSlot();
                        requestStart = System.nanoTime();
                        HttpResponse<String> response = sendQuoteRequest("TSLA");
                        long requestTime = (System.nanoTime() - requestStart) / 1_000_000;
                        requestTimeTotal += requestTime;
                        fastest = Math.min(fastest, requestTime);
                        slowest = Math.max(slowest, requestTime);
                        if (response.statusCode() == 200 && response.body().contains("\"c\":")) {
                            successfulRequests++;
                        }
                    } catch (Exception exception) {
                        long requestTime = 0;

                        if (requestStart > 0) {

                            requestTime = (System.nanoTime() - requestStart) / 1_000_000;
                        }
                        requestTimeTotal += requestTime;
                        fastest = Math.min(fastest, requestTime);

                        slowest = Math.max(slowest, requestTime);
                    }
                    long memoryUsed = runtime.totalMemory() - runtime.freeMemory();
                    memoryTotal += memoryUsed;
                    memoryPeak = Math.max( memoryPeak, memoryUsed );
                }
                long testTime = (System.nanoTime() - testStart) / 1_000_000;
                long cpuTime = osBean.getProcessCpuTime() - cpuStart;
                double averageRequestTime = (double) requestTimeTotal / numberOfRequests;
                double averageMemory = (double) memoryTotal / numberOfRequests / (1024 * 1024);
                double peakMemory = (double) memoryPeak / (1024 * 1024);

                double cpuUsage = 0;

                if (testTime > 0) {

                    cpuUsage = (cpuTime / 1_000_000_000.0) / (testTime / 1_000.0) * 100.0;


                }
                return new PerformanceResult( numberOfRequests,
                    successfulRequests, averageRequestTime, fastest, slowest, averageMemory, peakMemory, cpuUsage, testTime );
            }
            //shows test results
            @Override protected void done() {
                try {
                    PerformanceResult result = get();
                    String results = String.format( "JAVA PERFORMANCE TEST\n" + "========================================\n\n" + "Requests completed:      %d\n" + "Successful requests:     %d\n\n" + "Average request time:    %.2f ms\n" + "Fastest request:         %d ms\n" + "Slowest request:         %d ms\n\n" + "Average memory usage:     %.2f MB\n" + "Peak memory usage:        %.2f MB\n\n" + "Average CPU usage:        %.2f%%\n" + "Total test time:          %d ms\n",
                            result.totalRequests, result.successfulRequests, result.averageRequestTime, result.fastestRequest, result.slowestRequest, result.averageMemory, result.peakMemory, result.cpuUsage, result.totalTime );

                    performanceResults.setText(results);
                    performanceResults.setCaretPosition(0);
                    System.out.println(results);
                } catch (Exception exception) {
                    System.err.println( "Performance test failed: " + exception.getMessage() );
                }

            }
        }.execute();
    }
    private static class PerformanceResult {
        private final int totalRequests;
        private final long successfulRequests;
        private final double averageRequestTime;

        private final long fastestRequest;
        private final long slowestRequest;
        private final double averageMemory;

        private final double peakMemory;

        private final double cpuUsage;
        private final long totalTime;
        private PerformanceResult( int totalRequests, long successfulRequests,
                double averageRequestTime, long fastestRequest, long slowestRequest, double averageMemory, double peakMemory, double cpuUsage, long totalTime ) {

            this.totalRequests  =  totalRequests;


            this.successfulRequests = successfulRequests;
            this.averageRequestTime = averageRequestTime;
            this.fastestRequest = fastestRequest;
            this.slowestRequest = slowestRequest;
            this.averageMemory = averageMemory;
            this.peakMemory = peakMemory;
            this.cpuUsage = cpuUsage;
            this.totalTime = totalTime;
        }
    }
    //starts the app
    public static void main( String[] args ) {
        SwingUtilities.invokeLater(() -> {
            StockApp window = new StockApp();
            window.setVisible(true); });
    }
}

