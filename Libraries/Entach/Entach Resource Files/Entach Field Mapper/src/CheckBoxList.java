
import java.util.ArrayList;

import javax.swing.JPanel;

public class CheckBoxList
{
	private ArrayList<CheckBox> CheckBoxList = new ArrayList<CheckBox>();
	
	public CheckBoxList()
	{
		
	}
	
	public void addCheckBox(CheckBox inputCheckBox)
	{
		CheckBoxList.add(inputCheckBox);
	}
	
	public void removeCheckBox(int index, JPanel panel)
	{
		CheckBoxList.get(index).removeCheckBox(panel);
		CheckBoxList.remove(index);
	}
	
	public CheckBox getCheckBox(int index)
	{
		return CheckBoxList.get(index);
	}
	
	public int getListSize()
	{
		return CheckBoxList.size();
	}
	
	public void removeAllCheckBoxes(JPanel panel)
	{
		for (int index = 1; index < CheckBoxList.size(); index++) {
			CheckBoxList.get(index).removeCheckBox(panel);
		}
		if(CheckBoxList.size() != 0) {
			while (CheckBoxList.size() >= 1) {
				CheckBoxList.remove(CheckBoxList.size() - 1);
			}
		}
	}

	public ArrayList<CheckBox> getArrayList()
	{
		return CheckBoxList;
	}
}
