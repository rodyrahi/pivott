imputewidget = featureWidget
        self.impute_checkbox = popCheckBox('Impute Missing Values' , parent=self , widget=imputewidget)
        self.impute_checkbox.widget.imputeUI()
        self.featurescolumnLayout.addWidget(self.impute_checkbox.cb)
        self.impute_checkbox.cb.stateChanged.connect(lambda:self.impute_checkbox.visbility())



        outlier_checkbox = popCheckBox('Outlier Removing' , parent=self , widget=featureWidget )
        self.featurescolumnLayout.addWidget(outlier_checkbox.cb)
        outlier_checkbox.cb.stateChanged.connect(lambda:outlier_checkbox.visbility())

        
        encoding_checkbox = popCheckBox('Encoding Categorical' , parent=self , widget=featureWidget )
        encoding_checkbox.widget.encodeUI()
        self.featurescolumnLayout.addWidget(encoding_checkbox.cb)
        encoding_checkbox.cb.stateChanged.connect(lambda:encoding_checkbox.visbility())

