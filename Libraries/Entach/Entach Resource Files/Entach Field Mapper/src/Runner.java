
import java.awt.*;
import java.awt.event.*;
import java.awt.geom.AffineTransform;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.text.DecimalFormat;

import javax.imageio.ImageIO;
import javax.swing.*;

public class Runner extends JPanel implements KeyListener, MouseListener, MouseMotionListener, ActionListener
{	
	private static final long serialVersionUID = 1L;
	
	private BufferedImage FTCFieldImage, robotImage;
	
	private String fieldImageFilePath = "src/Images/FTC Field Image 2014.png";
	private String robotImageFilePath = "src/Images/robotImage.png";
	
	int xMouseCoord, yMouseCoord;
	int xMouseCoordClick, yMouseCoordClick;
	
	boolean mouseClicked;
	boolean shiftPressed;
	
	int robotImageAngle = 0;
	int robotImageWidth, robotImageHeight;
	double originalRobotImageWidth, originalRobotImageHeight;
	int fieldImageHeight, fieldImageWidth;
	
	CoordinateList goToPoints = new CoordinateList();
	CheckBoxList checkBoxes = new CheckBoxList();
	ImageGhostList imageGhosts = new ImageGhostList();
	
	ListOverseer listActions;
	
	private JButton submitPointsButton = new JButton("Submit Points");
	private JButton rotateLeft5DegreesButton = new JButton("Rotate Left 5 degrees");
	private JButton rotateRight5DegreesButton = new JButton("Rotate Right 5 degrees");
	private JButton clearAllPathsButton = new JButton("Clear All Paths");
	private JButton deleteLastPathButton = new JButton("Delete Last Path");
	private JButton toggleEnableAllAnglesButton = new JButton("Toggle enable all angles");
	
	private JTextField fieldSourceFileTextField = new JTextField(30); private JLabel fieldSourceFileLabel = new JLabel("Field Image file path");
	private JTextField robotSourceFileTextField = new JTextField(30); private JLabel robotSourceFileLabel = new JLabel("Robot Image file path");
	private JTextField fieldCMwidth = new JTextField(4); private JLabel fieldCMwidthLabel = new JLabel("");
	private JTextField robotCMwidth = new JTextField(15); private JLabel robotCMwidthLabel = new JLabel("");
	private JTextField robotCMheight = new JTextField(15); private JLabel robotCMheightLabel = new JLabel("");
	private JTextField fieldLandmark1 = new JTextField(15);
	private JTextField fieldLandmark2 = new JTextField(15);
	
	public static void main(String args[])
	{		
		JFrame frame = new JFrame("Entach Field Mapper");
    	frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
//    	frame.setLayout(new BorderLayout());
    	
    	Runner runner = new Runner();
    	frame.add(runner, BorderLayout.CENTER);
    	
    	frame.setSize(1440, 900);
    	frame.setVisible(true);
    	
    	frame.setBackground(Color.WHITE);
	}
	
	public Runner()
	{	
		this.setLayout(null);
		
		try
		{
			FTCFieldImage = ImageIO.read(new File(fieldImageFilePath));
			robotImage = ImageIO.read(new File(robotImageFilePath));
		}
		catch (IOException e) {
			e.printStackTrace();
		}
		
		originalRobotImageWidth = robotImage.getWidth();
		originalRobotImageHeight = robotImage.getHeight();
		robotImageWidth = robotImage.getWidth(); 
		robotImageHeight = robotImage.getHeight();
		fieldImageWidth = FTCFieldImage.getWidth();
		fieldImageHeight = FTCFieldImage.getHeight();
		
		setSize(1440, 900);
		
		addKeyListener(this);	
		addMouseListener(this);
		addMouseMotionListener(this);
		
        setFocusable(true);
        requestFocusInWindow();
        
        submitPointsButton.addActionListener(this); 		submitPointsButton.setBounds(1000, 15, 200, 45); 			this.add(submitPointsButton);
        rotateLeft5DegreesButton.addActionListener(this); 	rotateLeft5DegreesButton.setBounds(1000, 65, 200, 45); 		this.add(rotateLeft5DegreesButton);
        rotateRight5DegreesButton.addActionListener(this);	rotateRight5DegreesButton.setBounds(1000, 115, 200, 45);	this.add(rotateRight5DegreesButton);
        clearAllPathsButton.addActionListener(this); 		clearAllPathsButton.setBounds(1000, 165, 200, 45); 			this.add(clearAllPathsButton);
        deleteLastPathButton.addActionListener(this); 		deleteLastPathButton.setBounds(1000, 215, 200, 45); 		this.add(deleteLastPathButton);
        toggleEnableAllAnglesButton.addActionListener(this);toggleEnableAllAnglesButton.setBounds(1000, 265, 200, 45); 	this.add(toggleEnableAllAnglesButton);
        
        addMapperParameterTextField(fieldSourceFileTextField, fieldSourceFileLabel, FTCFieldImage, 50, fieldImageHeight + 80, 200, 35, 50, fieldImageHeight + 60, 200, 20);
        addMapperParameterTextField(robotSourceFileTextField, robotSourceFileLabel, robotImage, 50, fieldImageHeight + 140, 200, 35, 50, fieldImageHeight + 120, 200, 20);
        addMapperParameterTextField(fieldCMwidth, fieldCMwidthLabel, fieldImageWidth / 2, fieldImageHeight + 200, 100, 35, fieldImageWidth / 2 + 110, fieldImageHeight + 200, 200, 35);
        	JLabel fieldCMwidthDesciptor = new JLabel("Field Width in cm"); fieldCMwidthDesciptor.setBounds(fieldImageWidth / 2, fieldImageHeight + 175, 200, 35); this.add(fieldCMwidthDesciptor);
        addMapperParameterTextField(robotCMwidth, robotCMwidthLabel, 300, fieldImageHeight + 80, 240, 35, 300, fieldImageHeight + 60, 200, 20);
        addMapperParameterTextField(robotCMheight, robotCMheightLabel, 300, fieldImageHeight + 140, 240, 35, 300, fieldImageHeight + 120, 200, 20);
        addMapperParameterTextField(fieldLandmark1, new JLabel(""), fieldImageWidth / 2, fieldImageHeight + 5, 100, 35, 0, 0, 0, 0);
        addMapperParameterTextField(fieldLandmark2, new JLabel(""), fieldImageWidth + 5, fieldImageHeight / 2, 100, 35, 0, 0, 0, 0);
        
		//call step() 60 fps
		Timer timer = new Timer(1000/60, this);
		timer.start();
	}
	
	private void addMapperParameterTextField(final JTextField textField, JLabel label, final BufferedImage image, int xTextField, int yTextField, int widthTextField, int heightTextField, int xLabel, int yLabel, int widthLabel, int heightLabel)
	{
		label.setBounds(xLabel, yLabel, widthLabel, heightLabel); this.add(label);
		textField.addActionListener(this); textField.setBounds(xTextField, yTextField, widthTextField, heightTextField); this.add(textField);
		if (image.equals(robotImage))
		{
			textField.setText(robotImageFilePath);
			textField.addActionListener(new ActionListener()
			{
	            public void actionPerformed(ActionEvent e) {
	            	String filePath = textField.getText();
	            	System.out.println(filePath);
	            	
	            	robotImage = null;
	        		try {
	        			robotImage = ImageIO.read(new File(filePath));
	        		}
	            	catch (IOException e1) {	}
	            }
	        });
		}
		else if (image.equals(FTCFieldImage))
		{
			textField.setText(fieldImageFilePath);
			textField.addActionListener(new ActionListener()
			{
	            public void actionPerformed(ActionEvent e) {
	            	String filePath = textField.getText();
	            	System.out.println(filePath);
	            	
	            	FTCFieldImage = null;
	        		try {
	        			FTCFieldImage = ImageIO.read(new File(filePath));
	        		}
	            	catch (IOException e1) {	}
	        		
	        		fieldImageWidth = FTCFieldImage.getWidth();
	        		fieldImageHeight = FTCFieldImage.getHeight();
	            }
	        });
		}
	}
	
	private void addMapperParameterTextField(final JTextField textField, JLabel label, int xTextField, int yTextField, int widthTextField, int heightTextField, int xLabel, int yLabel, int widthLabel, int heightLabel)
	{
		label.setBounds(xLabel, yLabel, widthLabel, heightLabel);
		textField.addActionListener(this); textField.setBounds(xTextField, yTextField, widthTextField, heightTextField); this.add(textField);
		
		DecimalFormat df = new DecimalFormat("0.000");
		if (textField.equals(fieldCMwidth))
		{			
			textField.setText(String.valueOf(df.format(432 / Coordinate.getPixelsToCM())));
			fieldCMwidthLabel.setText(String.valueOf(df.format(Coordinate.getPixelsToCM())) + " pixels / cm");
			textField.addActionListener(new ActionListener()
			{
				DecimalFormat df = new DecimalFormat("0.000");
	            public void actionPerformed(ActionEvent e) {
	            	String fieldCMWidthString = textField.getText();
	            	System.out.println(fieldCMWidthString);
	            	
	            	double fieldWidthCM = Double.parseDouble(fieldCMWidthString.trim());
	            	
	            	Coordinate.setPixelsToCM(432 / fieldWidthCM);
	            	
	            	fieldCMwidthLabel.setText(String.valueOf(df.format(432 / fieldWidthCM)) + " pixels / cm");
	            }
	        });
		}
		else if (textField.equals(robotCMwidth))
		{
			robotCMwidthLabel.setText("Robot Width in Pixels: " + String.valueOf(df.format(robotImageWidth)));
			robotCMwidth.setText("Width of Robot in cm: " + String.valueOf(df.format(robotImageWidth * Coordinate.getPixelsToCM())));
			textField.addFocusListener(new FocusListener()
			{
				DecimalFormat df = new DecimalFormat("0.000");
				
	            public void focusGained(FocusEvent e) {
	            	robotCMwidth.setText("");
	            }
	            
	            public void focusLost(FocusEvent e)
	            {
	            	if (robotCMwidth.getText().equals("")) {
	            		robotCMwidth.setText("Width of Robot in cm: " + String.valueOf(df.format(robotImageWidth * Coordinate.getPixelsToCM())));
	            	}
	            	else
	            	{
		            	String robotCMWidthString = textField.getText();
		            	double robotWidthPixel = Double.parseDouble(robotCMWidthString.trim()) / Coordinate.getPixelsToCM();
		            	robotImageWidth = (int) (robotWidthPixel);
		            	
		            	robotCMwidthLabel.setText("Robot Width in Pixels: " + String.valueOf(df.format(robotImageWidth)));
	            	}
	            }
	        });
			textField.addActionListener(new ActionListener()
			{
	            public void actionPerformed(ActionEvent e)
	            {
	            	DecimalFormat df = new DecimalFormat("0.000");
	            	
	            	String robotCMWidthString = textField.getText();
	            	double robotWidthPixel = Double.parseDouble(robotCMWidthString.trim()) / Coordinate.getPixelsToCM();
	            	robotImageWidth = (int) (robotWidthPixel);
	            	
	            	robotCMwidthLabel.setText("Robot Width in Pixels: " + String.valueOf(df.format(robotImageWidth)));
	            	requestFocusInWindow();
	            	
	            	robotCMwidth.setText("Width of Robot in cm: " + String.valueOf(df.format(robotImageWidth * Coordinate.getPixelsToCM())));
	            }
	        });
		}
		
		else if (textField.equals(robotCMheight))
		{
			robotCMheightLabel.setText("Robot Height in Pixels: " + String.valueOf(df.format(robotImageHeight)));
			robotCMheight.setText("Height of Robot in cm: " + String.valueOf(df.format(robotImageHeight * Coordinate.getPixelsToCM())));
			textField.addFocusListener(new FocusListener()
			{
				DecimalFormat df = new DecimalFormat("0.000");
				
	            public void focusGained(FocusEvent e) {
	            	robotCMheight.setText("");
	            }
	            
	            public void focusLost(FocusEvent e) {
	            	if (robotCMheight.getText().equals("")) {
	            		robotCMheight.setText("Height of Robot in cm: " + String.valueOf(df.format(robotImageHeight * Coordinate.getPixelsToCM())));
	            	}
	            	else
	            	{
		            	String robotCMheightString = textField.getText();
		            	double robotheightPixel = Double.parseDouble(robotCMheightString.trim()) / Coordinate.getPixelsToCM();
		            	robotImageHeight = (int) (robotheightPixel);
		            	
		            	robotCMheightLabel.setText("Robot Height in Pixels: " + String.valueOf(df.format(robotImageHeight)));
	            	}
	            }
	        });
			textField.addActionListener(new ActionListener()
			{
	            public void actionPerformed(ActionEvent e)
	            {
	            	DecimalFormat df = new DecimalFormat("0.000");
	            	
	            	String robotCMHeightString = textField.getText();
	            	double robotHeightPixel = Double.parseDouble(robotCMHeightString.trim()) / Coordinate.getPixelsToCM();
	            	robotImageHeight = (int) (robotHeightPixel);
	            	
	            	robotCMheightLabel.setText("Robot Height in Pixels: " + String.valueOf(df.format(robotImageHeight)));
	            	
	            	requestFocusInWindow();
	            	robotCMheight.setText("Height of Robot in cm: " + String.valueOf(df.format(robotImageHeight * Coordinate.getPixelsToCM())));
	            }
	        });
		}
		else if (textField.equals(fieldLandmark1))
		{
			fieldLandmark1.setText("Landmark 1");
			
			textField.addFocusListener(new FocusListener()
			{
	            public void focusGained(FocusEvent e) {
	            	if (fieldLandmark1.getText().equals("Landmark 1")) {
	            		fieldLandmark1.setText("");
	            	}
	            }
	            
	            public void focusLost(FocusEvent e) {
	            	if (fieldLandmark1.getText().equals("")) {
	            		fieldLandmark1.setText("Landmark 1");
	            	}
	            }
			});
		}
		else if (textField.equals(fieldLandmark2))
		{
			fieldLandmark2.setText("Landmark 2");
			
			textField.addFocusListener(new FocusListener()
			{
	            public void focusGained(FocusEvent e) {
	            	if (fieldLandmark2.getText().equals("Landmark 2")) {
	            		fieldLandmark2.setText("");
	            	}
	            }
	            
	            public void focusLost(FocusEvent e) {
	            	if (fieldLandmark2.getText().equals("")) {
	            		fieldLandmark2.setText("Landmark 2");
	            	}
	            }
			});
		}
		
		this.add(label);
	}
	
	public void actionPerformed(ActionEvent e)
	{
		step();
		
		Object src = e.getSource();
	    if (src == submitPointsButton) {
	    	listActions.submitResults(fieldImageHeight, this);
	    }
	    else if (src == rotateLeft5DegreesButton){
	    	if (shiftPressed == false)
				rotateRobotBy(5);
			else
				rotateRobotBy(45);
	    }
	    else if (src == rotateRight5DegreesButton){
	    	if (shiftPressed == false)
				rotateRobotBy(-5);
			else
				rotateRobotBy(-45);
	    }
	    else if (src == clearAllPathsButton){
	    	listActions.deleteAllPaths(this);
	    }
	    else if (src == deleteLastPathButton){
	    	listActions.deleteLastPath(this);
	    }
	    else if (src == toggleEnableAllAnglesButton)
	    {
	    	boolean allcheckBoxesChecked = true;
			
			for (int index = 1; index < checkBoxes.getArrayList().size(); index++) {
				if (checkBoxes.getArrayList().get(index).getIsChecked() == false) {
					allcheckBoxesChecked = false;
				}
			}
			
			if (allcheckBoxesChecked == true) {
				for (int index = 1; index < checkBoxes.getArrayList().size(); index++)
				{
					checkBoxes.getArrayList().get(index).toggleIsChecked();
					imageGhosts.getImageGhost(index).toggleIsHidden();
				}
			}
			else {
				for (int index = 1; index < checkBoxes.getArrayList().size(); index++)
				{
					checkBoxes.getArrayList().get(index).setIsChecked(true);
					imageGhosts.getImageGhost(index).setIsHidden(true);
				}
			}
	    }
	}
	
	public void step()
	{		
		repaint();
	}
	
	public void paintComponent(Graphics g)
	{
		super.paintComponent(g);
		
		Graphics2D g2 = (Graphics2D) g;
		
		g.setColor(Color.WHITE);
		g.fillRect(0, 0, 4000, 4000);
		
		AffineTransform fieldImageTransform = new AffineTransform();
		fieldImageTransform.scale(432 / (double)fieldImageWidth, 432 / (double)fieldImageHeight);
		g2.drawImage(FTCFieldImage, fieldImageTransform, null);
		
		g.setColor(Color.BLACK);
		g.drawRect(0, 0, 904, 432 + 50);
//		g.drawString("Mouse clicked at (" + xMouseCoordClick + "," + yMouseCoordClick + ")",0, 500);
//		
//		g.drawString("Mouse is located at (" + (xMouseCoord) + "," + (FTCFieldImage.getHeight(modalComp) - yMouseCoord) + ")",0, 515);
		
		if (xMouseCoord > 0 + robotImageWidth / 2 && xMouseCoord < 432 - robotImageHeight / 2 && yMouseCoord > 0 + robotImageWidth / 2 && yMouseCoord < 432 - robotImageHeight / 2)
		{		
			AffineTransform turn = new AffineTransform();
			
			Coordinate correctedCoordinate = new Coordinate(xMouseCoordClick, yMouseCoordClick);
			
			if (mouseClicked == true)
			{
				if (shiftPressed == true && goToPoints.getListSize() >= 1)
				{
					correctedCoordinate = correctedCoordinate.getAngleCorrectedCoordinate(goToPoints.getArrayList().get(goToPoints.getListSize() - 1), xMouseCoord, yMouseCoord);
					goToPoints.addCoordinate(new Coordinate(correctedCoordinate.getX(), correctedCoordinate.getY()));
					imageGhosts.addImageGhost(new ImageGhost("robotImage.png", (int)correctedCoordinate.getX() - robotImageWidth / 2, (int)correctedCoordinate.getY() - robotImageHeight / 2, robotImageAngle, robotImageWidth, robotImageHeight));
				}
				else
				{
					goToPoints.addCoordinate(new Coordinate(xMouseCoordClick, yMouseCoordClick));
					imageGhosts.addImageGhost(new ImageGhost("robotImage.png", xMouseCoordClick - robotImageWidth / 2, yMouseCoordClick - robotImageHeight / 2, robotImageAngle, robotImageWidth, robotImageHeight));
				}
				
				if (checkBoxes.getArrayList().size() == 0)
					checkBoxes.getArrayList().add(null);
				else
					checkBoxes.addCheckBox(new CheckBox(new Point(790, 10 + (goToPoints.getListSize()) * 15), new Point(815, 25 + (goToPoints.getListSize()) * 15), this)); //803, 23 + 
			}
			
			if (shiftPressed == true && goToPoints.getListSize() >= 1)
			{
				correctedCoordinate = correctedCoordinate.getAngleCorrectedCoordinate(goToPoints.getArrayList().get(goToPoints.getListSize() - 1), xMouseCoord, yMouseCoord);
				turn.translate(correctedCoordinate.getX() - robotImageWidth / 2, correctedCoordinate.getY() - robotImageHeight / 2);
				turn.rotate(Math.toRadians((360 - robotImageAngle) + 90), robotImageWidth / 2, robotImageHeight / 2);
			}
			else
			{
				turn.translate(xMouseCoord - robotImageWidth / 2, yMouseCoord - robotImageHeight / 2);
				turn.rotate(Math.toRadians((360 - robotImageAngle) + 90), robotImageWidth / 2, robotImageHeight / 2);
			}
//			System.out.println("(double)robotImageWidth / originalRobotImageWidth: " + (double)robotImageWidth / originalRobotImageWidth);
			turn.scale((double)robotImageWidth / originalRobotImageWidth, (double)robotImageHeight / originalRobotImageHeight);
			g2.drawImage(robotImage, turn, null);
		}
		
		g.setColor(Color.GREEN);
		g.drawString(robotImageAngle + "",xMouseCoord - 10, yMouseCoord);
		g.setColor(Color.BLACK);
		g.drawString(robotImageAngle + "",xMouseCoord - 9, yMouseCoord + 1);
		
		g.drawString("Enable Angle",790,20);
		
		if (imageGhosts.getArrayList().size() > 0) {
			for (int index = 1; index < imageGhosts.getArrayList().size(); index++) {
				imageGhosts.getImageGhost(index).setIsHidden(!checkBoxes.getCheckBox(index).getIsChecked());
			}
		}
		
		listActions = new ListOverseer(goToPoints, checkBoxes, imageGhosts, this);
		
		imageGhosts.redrawImageGhosts(g, robotImage, (double)robotImageWidth / originalRobotImageWidth, (double)robotImageHeight / originalRobotImageHeight);
		goToPoints.redrawPath(g);
		goToPoints.drawGhostPath(g, xMouseCoord, yMouseCoord, shiftPressed);
		
		goToPoints.printContent(g, 432);
		imageGhosts.printAngles(g);
		
		mouseClicked = false;
	}
	
	public void rotateRobotBy (int degrees)
	{
		robotImageAngle += degrees;
		if (robotImageAngle >= 360)
			robotImageAngle -= 360;
		else if (robotImageAngle < 0)
			robotImageAngle += 360;
	}
	
	@Override
	public void keyPressed(KeyEvent e)
	{
//		System.out.println("key code: " + e.getKeyCode());
		
		if (e.getKeyCode() == 16) //shift
		{
			shiftPressed = true;
		}
		else if (e.getKeyCode() == 10) //enter
		{
			listActions.submitResults(432, this);
		}
		else if (e.getKeyCode() == 8) //backspace
		{
			listActions.deleteLastPath(this);
		}
		else if (e.getKeyCode() == 37) //left arrow
		{
			if (shiftPressed == false)
				rotateRobotBy(5);
			else
				rotateRobotBy(45);
		}
		else if (e.getKeyCode() == 39) //right arrow
		{
			if (shiftPressed == false)
				rotateRobotBy(-5);
			else
				rotateRobotBy(-45);
		}
		else if (e.getKeyCode() == 27) //escape
		{
			listActions.deleteAllPaths(this);
		}
	}

	@Override
	public void keyReleased(KeyEvent e)
	{
		if (e.getKeyCode() == 16)
		{
			shiftPressed = false;
		}
	}

	@Override
	public void keyTyped(KeyEvent e)
	{
		
	}

	@Override
	public void mouseClicked(MouseEvent e)
	{
		
	}

	@Override
	public void mouseEntered(MouseEvent e)
	{
		
	}

	@Override
	public void mouseExited(MouseEvent e)
	{
		
	}

	@Override
	public void mousePressed(MouseEvent e)
	{
		mouseClicked = true;
		
		xMouseCoordClick = e.getX();
		yMouseCoordClick = e.getY();
	}

	@Override
	public void mouseReleased(MouseEvent e)
	{
		mouseClicked = false;
		
		xMouseCoordClick += 10000;
		yMouseCoordClick += 10000;
	}

	@Override
	public void mouseDragged(MouseEvent e)
	{
		xMouseCoord = e.getX();
		yMouseCoord = e.getY();
	}

	@Override
	public void mouseMoved(MouseEvent e)
	{
		xMouseCoord = e.getX();
		yMouseCoord = e.getY();
		
		requestFocusInWindow();
	}
}
