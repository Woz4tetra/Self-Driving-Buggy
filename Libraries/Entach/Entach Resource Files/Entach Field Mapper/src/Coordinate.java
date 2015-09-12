
public class Coordinate
{
	private double pointX, pointY;
	private static double pixelsToCM = 30.48 / 36;
	
	public Coordinate(double inputPointX, double inputPointY)
	{
		pointX = inputPointX;
		pointY = inputPointY;
	}
	public Coordinate(int inputPointX, int inputPointY)
	{
		pointX = inputPointX;
		pointY = inputPointY;
	}
	
	public double getX() { return pointX; }
	public double getY() { return pointY; }
	
	public void setX(double inputPointX) {
		pointX = inputPointX;
	}
	public void setY(double inputPointY) {
		pointY = inputPointY;
	}
	public void setCoordinate(double inputPointX, double inputPointY) {
		pointX = inputPointX; pointY = inputPointY;
	}
	public static void setPixelsToCM(double newConversion) {
		pixelsToCM = newConversion;
	}
	public static double getPixelsToCM() {
		return pixelsToCM;
	}
	
	
	
	public void convertCoordinate()
	{ // converts to centimeters 		
		this.setCoordinate(this.getX() * pixelsToCM, this.getY() * pixelsToCM);//convert pixels to centimeters
	}
	
	public double convertCoordinate(double numberToConvert)
	{ // converts to centimeters 
		return numberToConvert * pixelsToCM;
	}
	
	public void deconvertCoordinate() {
		this.setCoordinate(this.getX() / pixelsToCM, this.getY() / pixelsToCM);
	}
	
	public double deconvertCoordinate(double numberToConvert) { // converts to centimeters 
		return numberToConvert / pixelsToCM;
	}
	
	public Coordinate getAngleCorrectedCoordinate(Coordinate previousCoord, double currentMouseX, double currentMouseY)
	{
		double mouseAngle = Math.atan2(currentMouseX - previousCoord.getX(), currentMouseY - previousCoord.getY());// + Math.PI * 3/2;
		double mouseHypotenuse = Math.sqrt(Math.pow(previousCoord.getX() - currentMouseX,2) + Math.pow(previousCoord.getY() - currentMouseY,2));
		
		double correctedAngle = 0;
		
		if (mouseAngle < 0)
			mouseAngle += 2 * Math.PI;
		if (mouseAngle > 2 * Math.PI)
			mouseAngle -= 2 * Math.PI;
		
		if ((mouseAngle < Math.PI / 8 && mouseAngle > 0) || (mouseAngle > Math.PI * 15 / 8 && mouseAngle < Math.PI * 2))
			correctedAngle = 0;
		
		else if (mouseAngle > Math.PI / 8 && mouseAngle < Math.PI * 3 / 8)
			correctedAngle = Math.PI / 4;
		
		else if (mouseAngle > Math.PI * 3 / 8 && mouseAngle < Math.PI * 5 / 8)
			correctedAngle = Math.PI / 2;
		
		else if (mouseAngle > Math.PI * 5 / 8 && mouseAngle < Math.PI * 7 / 8)
			correctedAngle = Math.PI * 3 / 4;
		
		else if (mouseAngle > Math.PI * 7 / 8 && mouseAngle < Math.PI * 9 / 8)
			correctedAngle = Math.PI;
		
		else if (mouseAngle > Math.PI * 9 / 8 && mouseAngle < Math.PI * 11 / 8)
			correctedAngle = Math.PI * 5 / 4;
		
		else if (mouseAngle > Math.PI * 11 / 8 && mouseAngle < Math.PI * 13 / 8)
			correctedAngle = Math.PI * 3 / 2;
		
		else if (mouseAngle > Math.PI * 13 / 8 && mouseAngle < Math.PI * 15 / 8)
			correctedAngle = Math.PI * 7 / 4;
		
		correctedAngle -= Math.PI / 2;
		correctedAngle *= -1;
		
		Coordinate result = new Coordinate(Math.cos(correctedAngle) * mouseHypotenuse + previousCoord.getX(), Math.sin(correctedAngle) * mouseHypotenuse + previousCoord.getY());
		
		return result;
	}
}
