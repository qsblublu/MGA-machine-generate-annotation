package org.MGA;

import com.intellij.openapi.actionSystem.*;
import com.intellij.openapi.command.WriteCommandAction;
import com.intellij.openapi.editor.*;
import com.intellij.openapi.project.Project;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.InterruptedException;

/**
 * @author Qs
 */
public class GeneAnno extends AnAction {

    @Override
    public void actionPerformed(AnActionEvent event) {
        //Get all the required data from data keys
        Project project = event.getData(PlatformDataKeys.PROJECT);
        Editor editor = event.getData(PlatformDataKeys.EDITOR);

        //Document represents the file text selected by user
        Document document = editor.getDocument();
        SelectionModel selectionModel = editor.getSelectionModel();

        //Get the start position of the selection in the whole editor
        int start = selectionModel.getSelectionStart();

        //Get the text selected by user
        String selectedText = selectionModel.getSelectedText();

        //Get the line number that the start offset exists
        int curLineNumber = document.getLineNumber(start);
        int preLineStartOffset = start - document.getLineStartOffset(curLineNumber);

        //Get the insert position of generated annotation
        int insertOffset = start ;

        //The operation of doc must be thrown in Runnable api and handled within a new thread in IDEA
        Runnable runnable = new Runnable() {
            @Override
            public void run() {
                document.insertString(insertOffset, geneAnno(selectedText, preLineStartOffset));
            }
        };

        WriteCommandAction.runWriteCommandAction(project, runnable);
    }

    /**
     * Make action visible and available only when existing project and editor and some text in the editor
     *     is selected.
     * @param event
     */
    @Override
    public void update(AnActionEvent event) {
        //Get required data keys
        final Editor editor = event.getData(PlatformDataKeys.EDITOR);
        final SelectionModel selectionModel = editor.getSelectionModel();

        //Set visibility only in case of existing project and editor and if some text in the editor is selected
        event.getPresentation().setVisible(editor != null && selectionModel.hasSelection());
    }

    /**
     * Get the annotation of method codes by calling python script.
     * @param code
     * @return
     */
    public String geneAnno(String code, int offset) {
        //annotation contains the returned annotation of code
        String annotation = null;

        try {
            String[] args = new String[] {"python", "D:\\code\\java\\MGA\\lib\\geneAnno.py", code};
            Process process = Runtime.getRuntime().exec(args);
            //Get the output of python file with 'print' method
            BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream()));
            annotation = in.readLine();
            in.close();
            process.waitFor();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        annotation = formatAnno(annotation, offset);

        return annotation;
    }

    public String formatAnno(String annotation, int offset) {
        String[] annotations = annotation.split("\\.");
        String formatAnno = "/**\n";
        formatAnno += addSpace(offset);

        for (int i = 0; i < annotations.length; i++) {
            formatAnno += " * " + annotations[i].trim() + ".\n";
            formatAnno += addSpace(offset);
        }
        formatAnno += " */\n";
        formatAnno += addSpace(offset);

        return formatAnno;
    }

    public String addSpace(int spaceNum) {
        StringBuilder spaces = new StringBuilder();
        for (int i = 0; i < spaceNum; i++) {
            spaces.append(" ");
        }

        return spaces.toString();
    }
}